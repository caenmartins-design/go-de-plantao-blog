"""
Scraping direto das principais fontes sem RSS adequado:
FEBRASGO, ACOG, FIGO, WHO, Ministério da Saúde, Medscape, MedPage Today, Revista Femina.
"""

import hashlib
import re

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

FONTES = [
    # ── Sociedades Médicas ─────────────────────────────────────────────────────
    {
        "nome":    "FEBRASGO",
        "url":     "https://www.febrasgo.org.br/noticias",
        "seletor": "article, .noticia-item, .card, .post-item, li.views-row",
        "titulo":  "h2, h3, h4, .title, .field-title",
        "link":    "a",
        "data":    "time, .date, .data, span.views-field-created",
        "tipo":    "diretriz",
        "idioma":  "pt",
        "base":    "https://www.febrasgo.org.br",
    },
    {
        "nome":    "ACOG News",
        "url":     "https://www.acog.org/news",
        "seletor": "article, .news-item, .card, li[class*='news']",
        "titulo":  "h2, h3, .title, [class*='heading']",
        "link":    "a",
        "data":    "time, [class*='date'], span[class*='date']",
        "tipo":    "diretriz",
        "idioma":  "en",
        "base":    "https://www.acog.org",
    },
    {
        "nome":    "FIGO",
        "url":     "https://www.figo.org/news-and-resources",
        "seletor": "article, .news-item, .card, .resource-item",
        "titulo":  "h2, h3, h4, .title",
        "link":    "a",
        "data":    "time, .date, [class*='date']",
        "tipo":    "diretriz",
        "idioma":  "en",
        "base":    "https://www.figo.org",
    },
    {
        "nome":    "WHO — Women's Health",
        "url":     "https://www.who.int/news?healthtopics=women's-health",
        "seletor": "li.list-view--item, article, .sf-news-list__item",
        "titulo":  "h3, h4, .list-view--item__heading",
        "link":    "a",
        "data":    "time, span.timestamp, .date",
        "tipo":    "diretriz",
        "idioma":  "en",
        "base":    "https://www.who.int",
    },
    {
        "nome":    "Ministério da Saúde",
        "url":     "https://www.gov.br/saude/pt-br/assuntos/noticias",
        "seletor": "article, .tileItem, .summary",
        "titulo":  "h2, h3, .tileHeadline, .summary-title",
        "link":    "a",
        "data":    "span.documentByLine, time, .data",
        "tipo":    "diretriz",
        "idioma":  "pt",
        "base":    "https://www.gov.br",
    },
    # ── Portais de Notícias Médicas ────────────────────────────────────────────
    {
        "nome":    "Medscape OB/GYN",
        "url":     "https://www.medscape.com/obgyn",
        "seletor": "article, .card, .list-item, .news-item",
        "titulo":  "h2, h3, h4, .title, [class*='title']",
        "link":    "a",
        "data":    "time, .date, [class*='date']",
        "tipo":    "noticia",
        "idioma":  "en",
        "base":    "https://www.medscape.com",
    },
    {
        "nome":    "MedPage Today — OB/GYN",
        "url":     "https://www.medpagetoday.com/ob-gyn",
        "seletor": "article, .item, li[class*='story']",
        "titulo":  "h2, h3, h4, .title, [class*='hed']",
        "link":    "a",
        "data":    "time, .dateline, [class*='date']",
        "tipo":    "noticia",
        "idioma":  "en",
        "base":    "https://www.medpagetoday.com",
    },
    # ── Revista Femina ─────────────────────────────────────────────────────────
    {
        "nome":    "Revista Femina",
        "url":     "https://www.revistafemina.com.br/artigos",
        "seletor": "article, .artigo-item, .post, .card",
        "titulo":  "h2, h3, .entry-title, .post-title",
        "link":    "a",
        "data":    "time, .post-date, .entry-date, .data",
        "tipo":    "artigo_cientifico",
        "idioma":  "pt",
        "base":    "https://www.revistafemina.com.br",
    },
]


def buscar_scraping() -> list:
    """Raspa todas as fontes configuradas."""
    artigos = []
    for fonte in FONTES:
        try:
            items = _raspar(fonte)
            print(f"Scraping [{fonte['nome']}]: {len(items)} artigos")
            artigos.extend(items)
        except Exception as e:
            print(f"Scraping [{fonte['nome']}] erro: {e}")
    return artigos


def _raspar(fonte: dict) -> list:
    r = requests.get(fonte["url"], headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    artigos = []
    for item in soup.select(fonte["seletor"])[:12]:
        tag_titulo = item.select_one(fonte["titulo"])
        tag_link   = item.select_one(fonte["link"])
        tag_data   = item.select_one(fonte.get("data", "time"))

        titulo = tag_titulo.get_text(strip=True) if tag_titulo else ""
        link   = tag_link.get("href", "") if tag_link else ""
        data   = tag_data.get_text(strip=True) if tag_data else ""

        if not titulo or len(titulo) < 10:
            continue

        # Normaliza URL relativa
        if link and not link.startswith("http"):
            base = fonte.get("base", "")
            link = base + ("" if link.startswith("/") else "/") + link

        # Resumo: tenta pegar o próximo parágrafo ou descrição
        resumo = ""
        for tag in ("p", ".summary", ".excerpt", ".description", "[class*='lead']"):
            el = item.select_one(tag)
            if el and el.get_text(strip=True):
                resumo = el.get_text(strip=True)[:500]
                break

        artigos.append({
            "id":          f"scraping_{hashlib.md5(link.encode()).hexdigest()[:12]}",
            "titulo":      titulo,
            "fonte":       fonte["nome"],
            "url":         link,
            "data":        data,
            "resumo_bruto": resumo,
            "tipo":        fonte["tipo"],
            "idioma":      fonte["idioma"],
        })

    return artigos
