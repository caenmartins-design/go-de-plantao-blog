#!/usr/bin/env python3
"""
Go de Plantão — Script de publicação automática
Uso: chamado automaticamente pelo Claude Code após gerar cada artigo.
"""

import os, re, json, shutil, subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR   = Path(__file__).parent
ARTIGOS    = BASE_DIR / "artigos"
REFERENCES = BASE_DIR / "assets" / "references"
INDEX      = BASE_DIR / "index.html"
TEMPLATE   = ARTIGOS / "_template.html"
META_FILE  = BASE_DIR / "artigos.json"

COURSE_URL = "https://med.estrategia.com/concursos/cursos/cursos-de-ginecologia-e-obstetricia"
COUPON     = "GODEPLANTAO"


def slugify(text: str) -> str:
    text = text.lower().strip()
    for src, dst in [("ã","a"),("â","a"),("á","a"),("à","a"),("ä","a"),
                     ("ê","e"),("é","e"),("è","e"),("í","i"),("ó","o"),
                     ("ô","o"),("õ","o"),("ú","u"),("ü","u"),("ç","c"),("ñ","n")]:
        text = text.replace(src, dst)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:80]


def estimate_read_time(html: str) -> int:
    return 5


def build_tags_html(tags: list) -> str:
    return " ".join(f'<span class="tag">{t}</span>' for t in tags)


def build_reference_html(slug: str, reference_title: str) -> str:
    return f"""
    <div class="article-reference">
      <div class="ref-inner">
        <span class="ref-icon">📄</span>
        <div class="ref-info">
          <p class="ref-label">Artigo original</p>
          <p class="ref-title">{reference_title}</p>
        </div>
        <a class="ref-btn" href="../assets/references/{slug}.pdf" target="_blank" rel="noopener">⬇ Baixar PDF</a>
      </div>
    </div>"""


def build_card_html(article: dict) -> str:
    return f"""
        <article class="article-card">
          <div class="card-body">
            <div class="card-meta">
              <span class="card-category">{article['category']}</span>
              <span>{article['date']}</span>
            </div>
            <h2 class="card-title">{article['title']}</h2>
            <p class="card-excerpt">{article['excerpt']}</p>
            <div class="card-footer">
              <a class="read-more" href="artigos/{article['slug']}.html">Leia o artigo →</a>
              <span class="read-time">⏱ {article['read_time']} min</span>
            </div>
          </div>
        </article>"""


def load_meta() -> list:
    if META_FILE.exists():
        return json.loads(META_FILE.read_text(encoding="utf-8"))
    return []


def save_meta(articles: list):
    META_FILE.write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")


def rebuild_index(articles: list):
    html = INDEX.read_text(encoding="utf-8")
    cards = "\n".join(build_card_html(a) for a in reversed(articles))
    START = '<div class="articles-grid" id="articles-grid">'
    SENTINEL = "<!-- /articles-grid -->"
    start_idx = html.index(START) + len(START)
    end_idx = html.index(SENTINEL)
    html = html[:start_idx] + "\n" + cards + "\n\n      " + html[end_idx:]
    INDEX.write_text(html, encoding="utf-8")


def publish_article(
    title: str,
    category: str,
    body_html: str,
    excerpt: str,
    tags: list = None,
    date: str = None,
    reference_pdf: str = None,
    reference_title: str = None,
) -> dict:
    """
    Publica um artigo no blog.

    Parâmetros
    ----------
    title           : Título do artigo
    category        : Categoria (ex: 'Pré-eclâmpsia', 'Urgências', 'Guidelines')
    body_html       : Corpo do artigo em HTML (sem <html>/<body>)
    excerpt         : Resumo curto (1-2 frases) para o card na home
    tags            : Lista de tags (opcional)
    date            : Data no formato 'DD/MM/AAAA' (usa hoje se omitido)
    reference_pdf   : Caminho local para o PDF de referência (opcional)
    reference_title : Título do artigo de referência para exibir no botão (opcional)

    Retorna
    -------
    dict com slug, url_local e mensagem de sucesso
    """
    tags  = tags or []
    date  = date or datetime.now().strftime("%d/%m/%Y")
    slug  = slugify(title)
    rt    = estimate_read_time(body_html)

    # Copia PDF de referência se fornecido
    ref_html = ""
    if reference_pdf:
        src = Path(reference_pdf)
        if src.exists():
            REFERENCES.mkdir(parents=True, exist_ok=True)
            dest = REFERENCES / f"{slug}.pdf"
            shutil.copy2(src, dest)
            ref_title = reference_title or src.name
            ref_html  = build_reference_html(slug, ref_title)
            print(f"   PDF     : {dest.name}")
        else:
            print(f"⚠️  PDF não encontrado: {reference_pdf}")

    # Gera arquivo do artigo
    template = TEMPLATE.read_text(encoding="utf-8")
    page = (template
        .replace("{{TITLE}}",         title)
        .replace("{{CATEGORY}}",      category)
        .replace("{{DATE}}",          date)
        .replace("{{READ_TIME}}",     str(rt))
        .replace("{{EXCERPT}}",       excerpt)
        .replace("{{BODY}}",          body_html)
        .replace("{{TAGS}}",          build_tags_html(tags))
        .replace("{{REFERENCE_PDF}}", ref_html)
    )

    article_path = ARTIGOS / f"{slug}.html"
    article_path.write_text(page, encoding="utf-8")

    # Atualiza metadados
    articles = load_meta()
    articles = [a for a in articles if a["slug"] != slug]
    meta = {
        "slug":          slug,
        "title":         title,
        "category":      category,
        "excerpt":       excerpt,
        "date":          date,
        "read_time":     rt,
        "tags":          tags,
        "has_reference": bool(reference_pdf and Path(reference_pdf).exists()),
    }
    articles.append(meta)
    save_meta(articles)

    # Reconstrói index
    rebuild_index(articles)

    # Git: add → commit → push
    _git_push(title)

    url_local = f"artigos/{slug}.html"
    print(f"\n✅ Artigo publicado: {title}")
    print(f"   Arquivo : {article_path}")
    print(f"   URL     : {url_local}")
    return {"slug": slug, "url_local": url_local, "title": title}


def _git_push(commit_msg: str):
    cmds = [
        ["git", "-C", str(BASE_DIR), "add", "-A"],
        ["git", "-C", str(BASE_DIR), "commit", "-m", f"post: {commit_msg}"],
        ["git", "-C", str(BASE_DIR), "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            print(f"⚠️  git: {result.stderr.strip() or result.stdout.strip()}")
