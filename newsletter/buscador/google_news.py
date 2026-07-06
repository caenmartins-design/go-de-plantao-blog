"""
Busca notícias via Google News RSS.
Agrega automaticamente resultados de Medscape, MedPage Today, ACOG, FEBRASGO,
FIGO, WHO, Ministério da Saúde, Folha, G1, BBC Brasil e muito mais.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import feedparser
import requests

from config import DIAS_RETROATIVOS
from buscador.fontes import KEYWORDS_OBGYN

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Consultas em inglês e português — cada uma agrega dezenas de fontes via Google News
QUERIES = [
    # ── Científico / Diretrizes internacionais ─────────────────────────────────
    {"q": "obstetrics gynecology guideline women health",  "idioma": "en", "tipo": "diretriz"},
    {"q": "ACOG practice bulletin obstetrics",             "idioma": "en", "tipo": "diretriz"},
    {"q": "WHO maternal health pregnancy 2025 2026",       "idioma": "en", "tipo": "diretriz"},
    {"q": "obstetrics gynecology new study research",      "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "preeclampsia pregnancy treatment outcomes",     "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "endometriosis treatment surgery outcomes",      "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "maternal mortality pregnancy outcomes study",   "idioma": "en", "tipo": "noticia"},
    {"q": "ovarian cancer cervical cancer treatment",      "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "IVF fertility reproductive medicine study",     "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "menopause hormone therapy women study",         "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "pregnancy complication gestational diabetes",   "idioma": "en", "tipo": "artigo_cientifico"},
    {"q": "ob-gyn women health Medscape MedPage",          "idioma": "en", "tipo": "noticia"},
    # ── Português / Brasil ─────────────────────────────────────────────────────
    {"q": "ginecologia obstetrícia estudo pesquisa",       "idioma": "pt", "tipo": "artigo_cientifico"},
    {"q": "FEBRASGO diretriz ginecologia 2025",            "idioma": "pt", "tipo": "diretriz"},
    {"q": "Ministério Saúde gestação gravidez programa",   "idioma": "pt", "tipo": "diretriz"},
    {"q": "pré-eclâmpsia gravidez tratamento Brasil",      "idioma": "pt", "tipo": "artigo_cientifico"},
    {"q": "câncer ginecológico mama útero tratamento",     "idioma": "pt", "tipo": "noticia"},
    {"q": "saúde mulher parto pré-natal Brasil 2025",      "idioma": "pt", "tipo": "noticia"},
    {"q": "ANVISA medicamento ginecologia aprovação",      "idioma": "pt", "tipo": "noticia"},
    {"q": "endometriose mioma útero tratamento",           "idioma": "pt", "tipo": "artigo_cientifico"},
]


def buscar_google_news(dias=DIAS_RETROATIVOS, max_por_query=10):
    """Busca notícias GO em todas as queries do Google News."""
    artigos = []
    vistos = set()
    corte = datetime.now(timezone.utc) - timedelta(days=dias)

    for q in QUERIES:
        try:
            items = _buscar_query(q["q"], q["idioma"], max_por_query, corte)
            novos = [a for a in items if a["url"] not in vistos]
            vistos.update(a["url"] for a in novos)

            # Para feeds genéricos de notícia, filtra por relevância em GO
            if q["tipo"] == "noticia":
                novos = [a for a in novos if _relevante(a["titulo"] + " " + a["resumo_bruto"])]

            for a in novos:
                a["tipo"] = q["tipo"]
                a["idioma"] = q["idioma"]

            artigos.extend(novos)
            print(f"Google News [{q['q'][:50]}]: {len(novos)} artigos")
        except Exception as e:
            print(f"Google News [{q['q'][:45]}] erro: {e}")

    return artigos


def _buscar_query(query, idioma, max_items, corte):
    if idioma == "pt":
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    else:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"

    r = requests.get(url, headers=HEADERS, timeout=12)
    feed = feedparser.parse(r.content)

    artigos = []
    for entry in feed.entries[:max_items]:
        data_pub = _extrair_data(entry)
        if data_pub and data_pub < corte:
            continue

        titulo = entry.get("title", "").strip()
        resumo = _limpar_html(entry.get("summary", ""))
        link   = entry.get("link", "")

        if not titulo or not link:
            continue

        artigos.append({
            "id":           f"gnews_{hashlib.md5(link.encode()).hexdigest()[:12]}",
            "titulo":       titulo,
            "fonte":        _extrair_fonte(entry),
            "url":          link,
            "data":         data_pub.strftime("%d/%m/%Y") if data_pub else "",
            "resumo_bruto": resumo[:1000],
            "tipo":         "noticia",
            "idioma":       idioma,
        })

    return artigos


def _extrair_data(entry):
    import time as _time
    for campo in ("published_parsed", "updated_parsed"):
        t = entry.get(campo)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def _extrair_fonte(entry):
    """Tenta extrair o nome do veículo da tag <source> do Google News."""
    source = entry.get("source", {})
    if isinstance(source, dict):
        return source.get("title", "Google News")
    return str(source) if source else "Google News"


def _limpar_html(texto):
    import re
    return re.sub(r"<[^>]+>", " ", texto).strip()


def _relevante(texto):
    texto_lower = texto.lower()
    return any(kw.lower() in texto_lower for kw in KEYWORDS_OBGYN)
