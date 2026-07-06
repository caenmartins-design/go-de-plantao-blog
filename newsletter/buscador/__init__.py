"""
Módulo de busca — agrega quatro fontes complementares:
  1. PubMed API      → artigos científicos indexados (qualquer revista)
  2. CrossRef API    → artigos recentes do Lancet, BJOG, JAMA, ACOG, NEJM etc.
  3. Google News RSS → notícias de Medscape, MedPage, FEBRASGO, ACOG, WHO, MS etc.
  4. Scraping direto → FEBRASGO, ACOG, FIGO, Medscape, MedPage Today, Femina
"""

import json
from config import VISTOS_FILE
from buscador.pubmed       import buscar_pubmed
from buscador.crossref     import buscar_crossref
from buscador.google_news  import buscar_google_news
from buscador.scraper      import buscar_scraping


def buscar_tudo() -> list:
    todos = []

    print("\n── 1/4  PubMed ──────────────────────────────────────")
    todos += buscar_pubmed()

    print("\n── 2/4  CrossRef (Lancet, BJOG, JAMA, ACOG…) ───────")
    todos += buscar_crossref()

    print("\n── 3/4  Google News (Medscape, ACOG, FEBRASGO…) ─────")
    todos += buscar_google_news()

    print("\n── 4/4  Scraping direto (FEBRASGO, FIGO, WHO…) ──────")
    todos += buscar_scraping()

    # Remove duplicatas por URL
    vistos_url = set()
    unicos = []
    for a in todos:
        if a["url"] and a["url"] not in vistos_url:
            vistos_url.add(a["url"])
            unicos.append(a)

    print(f"\nTotal bruto: {len(todos)} | Únicos: {len(unicos)}")
    novos = _filtrar_vistos(unicos)
    print(f"Novos (não vistos antes): {len(novos)}\n")
    return novos


def marcar_vistos(artigos: list):
    vistos = _carregar_vistos()
    vistos.update(a["id"] for a in artigos)
    VISTOS_FILE.write_text(
        json.dumps(list(vistos), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _carregar_vistos() -> set:
    if VISTOS_FILE.exists():
        return set(json.loads(VISTOS_FILE.read_text(encoding="utf-8")))
    return set()


def _filtrar_vistos(artigos: list) -> list:
    vistos = _carregar_vistos()
    return [a for a in artigos if a["id"] not in vistos]
