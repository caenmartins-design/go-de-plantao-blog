"""
Busca artigos recentes nas principais revistas de GO via CrossRef API.
CrossRef indexa Lancet, BJOG, JAMA, ACOG Green Journal, etc. — gratuito, sem API key.
"""

import time
import requests
from datetime import datetime, timedelta
from config import DIAS_RETROATIVOS

HEADERS = {"User-Agent": "GOdePlantao-Newsletter/1.0 (mailto:contato@godeplantao.com.br)"}

# Principais revistas de GO com seus ISSNs
REVISTAS = [
    {"nome": "The Lancet",                           "issn": "0140-6736", "tipo": "artigo_cientifico"},
    {"nome": "BJOG",                                 "issn": "1471-0528", "tipo": "artigo_cientifico"},
    {"nome": "Obstetrics & Gynecology (ACOG)",       "issn": "0029-7844", "tipo": "artigo_cientifico"},
    {"nome": "JAMA",                                 "issn": "0098-7484", "tipo": "artigo_cientifico"},
    {"nome": "American Journal of Obs & Gynecology", "issn": "0002-9378", "tipo": "artigo_cientifico"},
    {"nome": "NEJM",                                 "issn": "0028-4793", "tipo": "artigo_cientifico"},
    {"nome": "Gynecologic Oncology",                 "issn": "0090-8258", "tipo": "artigo_cientifico"},
    {"nome": "Fertility and Sterility",              "issn": "0015-0282", "tipo": "artigo_cientifico"},
    {"nome": "Ultrasound in Obstetrics & Gynecology","issn": "0960-7692", "tipo": "artigo_cientifico"},
    {"nome": "Revista Femina (FEBRASGO)",            "issn": "0100-7203", "tipo": "artigo_cientifico"},
    {"nome": "BMJ",                                  "issn": "0959-8138", "tipo": "artigo_cientifico"},
]

BASE_URL = "https://api.crossref.org/journals/{issn}/works"
_TIMEOUT = 25
_MAX_TENTATIVAS = 2


def buscar_crossref(max_por_revista=5, dias=DIAS_RETROATIVOS):
    """Busca artigos recentes em cada revista via CrossRef API."""
    artigos = []
    data_corte = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

    for revista in REVISTAS:
        items = _buscar_com_retry(revista, max_por_revista, data_corte)
        for item in items:
            artigo = _parsear_item(item, revista)
            if artigo:
                artigos.append(artigo)
        print(f"CrossRef [{revista['nome']}]: {len(items)} artigos")
        time.sleep(0.5)

    return artigos


def _buscar_com_retry(revista, rows, data_corte):
    """Tenta buscar até _MAX_TENTATIVAS vezes com pausa entre tentativas."""
    for tentativa in range(_MAX_TENTATIVAS):
        try:
            return _buscar_revista(revista["issn"], rows, data_corte)
        except requests.exceptions.Timeout:
            if tentativa < _MAX_TENTATIVAS - 1:
                print(f"CrossRef [{revista['nome']}] timeout — tentando novamente...")
                time.sleep(3)
            else:
                print(f"CrossRef [{revista['nome']}] erro: timeout após {_MAX_TENTATIVAS} tentativas")
        except Exception as e:
            print(f"CrossRef [{revista['nome']}] erro: {e}")
            break
    return []


def _buscar_revista(issn, rows, data_corte):
    params = {
        "rows":   rows,
        "sort":   "published",
        "order":  "desc",
        "filter": f"from-pub-date:{data_corte}",
        "select": "DOI,title,abstract,author,published,container-title,URL,type",
    }
    r = requests.get(
        BASE_URL.format(issn=issn),
        params=params,
        headers=HEADERS,
        timeout=_TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get("message", {}).get("items", [])


def _parsear_item(item, revista):
    titulo_lista = item.get("title", [])
    if not titulo_lista:
        return None
    titulo = titulo_lista[0].strip()

    abstract_raw = item.get("abstract", "")
    import re
    abstract = re.sub(r"<[^>]+>", " ", abstract_raw).strip()

    autores = []
    for au in item.get("author", [])[:3]:
        nome = f"{au.get('family', '')} {au.get('given', '')}".strip()
        if nome:
            autores.append(nome)
    if len(item.get("author", [])) > 3:
        autores.append("et al.")

    pub = item.get("published", {})
    partes = pub.get("date-parts", [[]])[0]
    data = "/".join(str(p) for p in partes) if partes else ""

    doi = item.get("DOI", "")
    url = item.get("URL", f"https://doi.org/{doi}" if doi else "")

    return {
        "id":           f"crossref_{doi.replace('/', '_')}",
        "titulo":       titulo,
        "fonte":        revista["nome"],
        "url":          url,
        "data":         data,
        "resumo_bruto": abstract[:1500],
        "autores":      ", ".join(autores),
        "tipo":         revista["tipo"],
        "idioma":       "en",
    }
