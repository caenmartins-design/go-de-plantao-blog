"""Busca artigos recentes no PubMed via NCBI E-utilities (sem API key)."""

import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from config import DIAS_RETROATIVOS, MAX_POR_FONTE
from buscador.fontes import PUBMED_QUERY

ESEARCH_URL  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
EFETCH_URL   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def buscar_pubmed(max_results: int = MAX_POR_FONTE, dias: int = DIAS_RETROATIVOS) -> list[dict]:
    """Retorna lista de artigos do PubMed dos últimos `dias` dias."""
    ids = _buscar_ids(max_results, dias)
    if not ids:
        print("PubMed: nenhum ID encontrado.")
        return []
    print(f"PubMed: {len(ids)} artigos encontrados — buscando detalhes...")
    artigos = _buscar_detalhes(ids)
    return artigos


def _buscar_ids(max_results: int, dias: int) -> list[str]:
    data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y/%m/%d")
    params = {
        "db":      "pubmed",
        "term":    PUBMED_QUERY,
        "retmax":  max_results,
        "retmode": "json",
        "sort":    "pub date",
        "datetype":"pdat",
        "mindate": data_inicio,
        "maxdate": datetime.now().strftime("%Y/%m/%d"),
    }
    try:
        r = requests.get(ESEARCH_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"PubMed esearch erro: {e}")
        return []


def _buscar_detalhes(ids: list[str]) -> list[dict]:
    artigos = []
    lotes = [ids[i:i+10] for i in range(0, len(ids), 10)]
    for lote in lotes:
        params = {
            "db":      "pubmed",
            "id":      ",".join(lote),
            "rettype": "abstract",
            "retmode": "xml",
        }
        try:
            r = requests.get(EFETCH_URL, params=params, timeout=30)
            r.raise_for_status()
            artigos.extend(_parsear_xml(r.text))
            time.sleep(0.4)  # respeita limite da NCBI (3 req/s sem key)
        except Exception as e:
            print(f"PubMed efetch erro (lote {lote[0]}…): {e}")
    return artigos


def _parsear_xml(xml_text: str) -> list[dict]:
    artigos = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    for article in root.findall(".//PubmedArticle"):
        try:
            pmid = article.findtext(".//PMID", "")
            titulo = article.findtext(".//ArticleTitle", "Sem título")
            abstract_node = article.find(".//Abstract/AbstractText")
            abstract = abstract_node.text or "" if abstract_node is not None else ""

            # Múltiplos blocos de abstract (structured)
            abstract_parts = article.findall(".//AbstractText")
            if len(abstract_parts) > 1:
                abstract = " ".join(
                    (f"[{p.get('Label', '')}] " if p.get("Label") else "") + (p.text or "")
                    for p in abstract_parts
                )

            journal = article.findtext(".//Journal/Title", "")
            ano     = article.findtext(".//PubDate/Year", "")
            mes     = article.findtext(".//PubDate/Month", "")
            data_pub = f"{mes} {ano}".strip() if mes else ano

            autores = []
            for au in article.findall(".//Author")[:3]:
                sobrenome = au.findtext("LastName", "")
                nome = au.findtext("ForeName", "")
                if sobrenome:
                    autores.append(f"{sobrenome} {nome}".strip())
            if len(article.findall(".//Author")) > 3:
                autores.append("et al.")

            artigos.append({
                "id":      f"pubmed_{pmid}",
                "titulo":  titulo,
                "fonte":   f"PubMed — {journal}" if journal else "PubMed",
                "url":     f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "data":    data_pub,
                "resumo_bruto": abstract[:2000],
                "autores": ", ".join(autores),
                "tipo":    "artigo_cientifico",
                "idioma":  "en",
            })
        except Exception:
            continue

    return artigos
