"""Lê feeds RSS de revistas e portais de notícias médicas."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import requests

from config import DIAS_RETROATIVOS, MAX_POR_FONTE
from buscador.fontes import RSS_FEEDS, KEYWORDS_OBGYN

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}


def buscar_rss(dias: int = DIAS_RETROATIVOS, max_por_feed: int = MAX_POR_FONTE) -> list[dict]:
    """Varre todos os feeds RSS configurados e retorna artigos recentes."""
    artigos = []
    corte = datetime.now(timezone.utc) - timedelta(days=dias)

    for fonte in RSS_FEEDS:
        try:
            feed = _ler_feed(fonte["url"])
            count = 0
            for entry in feed.entries:
                if count >= max_por_feed:
                    break

                data_pub = _extrair_data(entry)

                # Filtra por data (pula se muito antigo)
                if data_pub and data_pub < corte:
                    continue

                titulo  = entry.get("title", "").strip()
                resumo  = _extrair_resumo(entry)
                url     = entry.get("link", "")

                # Feeds genéricos: filtra por palavras-chave GO
                if _e_feed_generico(fonte) and not _relevante_obgyn(titulo + " " + resumo):
                    continue

                artigos.append({
                    "id":          f"rss_{fonte['nome'].replace(' ', '_')}_{hash(url)}",
                    "titulo":      titulo,
                    "fonte":       fonte["nome"],
                    "url":         url,
                    "data":        data_pub.strftime("%d/%m/%Y") if data_pub else "",
                    "resumo_bruto": resumo[:1500],
                    "tipo":        fonte["tipo"],
                    "idioma":      fonte["idioma"],
                })
                count += 1

            print(f"RSS [{fonte['nome']}]: {count} artigos")
        except Exception as e:
            print(f"RSS [{fonte['nome']}] erro: {e}")

    return artigos


def _ler_feed(url: str) -> feedparser.FeedParserDict:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        return feedparser.parse(r.content)
    except Exception:
        return feedparser.parse(url)


def _extrair_data(entry) -> Optional[datetime]:
    for campo in ("published_parsed", "updated_parsed", "created_parsed"):
        t = entry.get(campo)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def _extrair_resumo(entry) -> str:
    for campo in ("summary", "description", "content"):
        val = entry.get(campo)
        if isinstance(val, list):
            val = val[0].get("value", "") if val else ""
        if val:
            # Remove tags HTML simples
            import re
            return re.sub(r"<[^>]+>", " ", val).strip()
    return ""


def _e_feed_generico(fonte: dict) -> bool:
    """Feeds genéricos (Reuters, BBC, Folha…) precisam filtragem extra."""
    genericos = {"Reuters Health", "BBC Brasil", "Folha Equilíbrio e Saúde",
                 "G1 Ciência e Saúde", "JAMA", "NEJM", "The Lancet",
                 "WHO News", "Agência Saúde (MS)"}
    return fonte["nome"] in genericos


def _relevante_obgyn(texto: str) -> bool:
    texto_lower = texto.lower()
    return any(kw.lower() in texto_lower for kw in KEYWORDS_OBGYN)
