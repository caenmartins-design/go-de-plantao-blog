#!/usr/bin/env python3
"""
Go de Plantão — Script de publicação automática
Uso: chamado automaticamente pelo Claude Code após gerar cada artigo.
"""

import os, re, json, subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR  = Path(__file__).parent
ARTIGOS   = BASE_DIR / "artigos"
INDEX     = BASE_DIR / "index.html"
TEMPLATE  = ARTIGOS / "_template.html"
META_FILE = BASE_DIR / "artigos.json"

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
    words = len(re.sub(r"<[^>]+>", "", html).split())
    return max(1, round(words / 200))


def build_tags_html(tags: list) -> str:
    return " ".join(f'<span class="tag">{t}</span>' for t in tags)


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
    html = re.sub(
        r"<!-- ARTICLES_PLACEHOLDER -->",
        cards if cards else "<!-- ARTICLES_PLACEHOLDER -->",
        html,
    )
    INDEX.write_text(html, encoding="utf-8")


def publish_article(
    title: str,
    category: str,
    body_html: str,
    excerpt: str,
    tags: list = None,
    date: str = None,
) -> dict:
    """
    Publica um artigo no blog.

    Parâmetros
    ----------
    title      : Título do artigo
    category   : Categoria (ex: 'Pré-eclâmpsia', 'Urgências', 'Guidelines')
    body_html  : Corpo do artigo em HTML (sem <html>/<body>)
    excerpt    : Resumo curto (1-2 frases) para o card na home
    tags       : Lista de tags (opcional)
    date       : Data no formato 'DD/MM/AAAA' (usa hoje se omitido)

    Retorna
    -------
    dict com slug, url_local e mensagem de sucesso
    """
    tags  = tags or []
    date  = date or datetime.now().strftime("%d/%m/%Y")
    slug  = slugify(title)
    rt    = estimate_read_time(body_html)

    # Gera arquivo do artigo
    template = TEMPLATE.read_text(encoding="utf-8")
    page = (template
        .replace("{{TITLE}}",     title)
        .replace("{{CATEGORY}}", category)
        .replace("{{DATE}}",      date)
        .replace("{{READ_TIME}}", str(rt))
        .replace("{{EXCERPT}}",   excerpt)
        .replace("{{BODY}}",      body_html)
        .replace("{{TAGS}}",      build_tags_html(tags))
    )

    article_path = ARTIGOS / f"{slug}.html"
    article_path.write_text(page, encoding="utf-8")

    # Atualiza metadados
    articles = load_meta()
    # Remove duplicata se slug já existe
    articles = [a for a in articles if a["slug"] != slug]
    meta = {
        "slug":      slug,
        "title":     title,
        "category":  category,
        "excerpt":   excerpt,
        "date":      date,
        "read_time": rt,
        "tags":      tags,
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


# ---------------------------------------------------------------------------
# Exemplo de uso direto (para testes)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    publish_article(
        title    = "Sulfato de Magnésio no Pós-Parto: 12h ou 24h na Pré-eclâmpsia Grave?",
        category = "Pré-eclâmpsia",
        excerpt  = "Um modelo de decisão analítica com 45.800 pacientes questiona o regime tradicional de 24 horas na profilaxia anticonvulsivante.",
        tags     = ["sulfato de magnésio", "pré-eclâmpsia", "pós-parto", "custo-efetividade", "eclâmpsia"],
        body_html="""
<p>O esquema tradicional de <strong>24 horas de sulfato de magnésio</strong> no pós-parto é amplamente
utilizado para profilaxia anticonvulsivante em pacientes com pré-eclâmpsia grave. No entanto, esse regime
possui baixa sustentação por evidências robustas, aumenta a exposição materna ao magnésio e impacta
negativamente o aleitamento materno, a deambulação precoce e o vínculo materno-neonatal.</p>

<h2>Desenho do Estudo</h2>
<p>Trata-se de um <strong>modelo de decisão analítica</strong> com uma coorte teórica de
<strong>45.800 pacientes</strong> com pré-eclâmpsia com características de gravidade. O objetivo foi avaliar
custo-efetividade, desfechos maternos, QALYs, toxicidade e impacto econômico dos dois regimes.</p>

<h2>Quando Ocorrem as Convulsões no Pós-Parto?</h2>
<ul>
  <li><strong>70%</strong> das convulsões ocorrem nas <strong>primeiras 12 horas</strong> pós-parto</li>
  <li><strong>17%</strong> ocorrem entre <strong>12 e 24 horas</strong> pós-parto</li>
</ul>
<p>Isso sugere que a maior parte do benefício anticonvulsivante ocorre na fase precoce do pós-parto.</p>

<h2>Resultados Clínicos</h2>
<table>
  <thead><tr><th>Desfecho</th><th>Regime 12h</th><th>Regime 24h</th></tr></thead>
  <tbody>
    <tr><td>Eclâmpsia</td><td>398 casos</td><td>312 casos</td></tr>
    <tr><td>Toxicidade por magnésio</td><td>2.089 casos</td><td>2.745 casos</td></tr>
    <tr><td>Mortes maternas</td><td>10,87</td><td>10,50</td></tr>
  </tbody>
</table>

<h2>Qualidade de Vida (QALYs)</h2>
<ul>
  <li>Regime 12h → <strong>255 QALYs</strong></li>
  <li>Regime 24h → <strong>238 QALYs</strong></li>
</ul>

<h2>Impacto Econômico</h2>
<ul>
  <li>12h → US$ 69,4 milhões</li>
  <li>24h → US$ 90,9 milhões</li>
  <li><strong>Economia líquida: US$ 21,5 milhões</strong></li>
</ul>
<p>O principal componente de custo foi a <strong>enfermagem 1:1</strong> — não o sulfato de magnésio em si.</p>

<h2>Número Necessário para Tratar (NNT)</h2>
<div class="callout">
  <div class="callout-title">Dado clínico importante</div>
  São necessárias <strong>531 pacientes</strong> em esquema de 24h para prevenir <strong>1 caso de eclâmpsia</strong>
  entre 12–24h pós-parto. Nesse grupo, ~7 apresentarão toxicidade por magnésio.
</div>

<h2>Análise de Sensibilidade</h2>
<p>O regime de 12h foi <strong>custo-efetivo em 89%</strong> das 10.000 simulações de Monte Carlo.
Os principais fatores que impactaram o modelo: custo de enfermagem, custo de UTI e toxicidade por magnésio.</p>

<h2>Conclusão Prática</h2>
<p>O regime de 12h de sulfato de magnésio no pós-parto:</p>
<ul>
  <li>Reduz custos em mais de US$ 21 milhões</li>
  <li>Reduz toxicidade por magnésio</li>
  <li>Melhora os QALYs maternos</li>
  <li>Mantém baixo impacto absoluto em eventos graves</li>
</ul>
<p>O estudo reforça a necessidade de <strong>individualizar a duração do sulfato de magnésio</strong> com base
na estratificação de risco de cada paciente.</p>

<p><em>Referência: Cost-Effectiveness Analysis: Postpartum Magnesium Sulfate (12 vs 24 Hours) for Seizure
Prophylaxis in Severe Preeclampsia.</em></p>
""",
    )
