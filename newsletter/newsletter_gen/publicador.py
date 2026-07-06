"""Publica a newsletter gerada na aba Newsletters do blog (commit + push automáticos)."""

import subprocess
from datetime import datetime
from pathlib import Path

from .gerador import _resumo_curto

BLOG_ROOT        = Path(__file__).parent.parent.parent
NEWSLETTERS_HTML = BLOG_ROOT / "newsletters.html"
NEWSLETTERS_DIR  = BLOG_ROOT / "newsletters"

GRID_MARKER = '<div class="articles-grid" id="newsletters-grid">'


def publicar_no_blog(resultado: dict, artigos_curados: list[dict], agora: datetime = None) -> dict:
    """
    Copia o HTML da newsletter para newsletters/, adiciona um card em
    newsletters.html e faz commit + push no repositório do blog.
    Retorna {"ok": bool, "erro": str opcional}.
    """
    agora = agora or datetime.now()
    data_arquivo = agora.strftime("%Y-%m-%d")
    data_exibicao = agora.strftime("%d/%m/%Y")

    NEWSLETTERS_DIR.mkdir(exist_ok=True)
    destino = NEWSLETTERS_DIR / f"{data_arquivo}.html"
    destino.write_text(Path(resultado["caminho_html"]).read_text(encoding="utf-8"), encoding="utf-8")

    destaque = next((a for a in artigos_curados if a.get("destaque")), artigos_curados[0])
    excerpt = f"Destaque: {destaque.get('titulo_pt', destaque.get('titulo',''))}. " + \
        _resumo_curto(destaque.get("resumo", ""), 180)
    read_time = max(3, round(sum(len(a.get("resumo", "").split()) for a in artigos_curados) / 200))

    _inserir_card(resultado["semana"], data_exibicao, excerpt, read_time, data_arquivo)

    return _commit_e_push(data_arquivo)


def _inserir_card(semana: str, data_exibicao: str, excerpt: str, read_time: int, data_arquivo: str) -> None:
    html = NEWSLETTERS_HTML.read_text(encoding="utf-8")

    card = f"""
        <article class="article-card">
          <div class="card-body">
            <div class="card-meta">
              <span class="card-category">Newsletter</span>
              <span>{data_exibicao}</span>
            </div>
            <h2 class="card-title">Semana de {semana}</h2>
            <p class="card-excerpt">{excerpt}</p>
            <div class="card-footer">
              <a class="read-more" href="newsletters/{data_arquivo}.html" target="_blank" rel="noopener">Ler newsletter →</a>
              <span class="read-time">⏱ {read_time} min</span>
            </div>
          </div>
        </article>
"""

    html = html.replace(GRID_MARKER, GRID_MARKER + card, 1)
    NEWSLETTERS_HTML.write_text(html, encoding="utf-8")
    print(f"✓ newsletters.html atualizado com a edição de {semana}")


def _commit_e_push(data_arquivo: str) -> dict:
    def git(*args):
        return subprocess.run(["git", *args], cwd=BLOG_ROOT, capture_output=True, text=True)

    git("fetch", "origin")
    rebase = git("rebase", "origin/main")
    if rebase.returncode != 0:
        git("rebase", "--abort")
        erro = "Conflito ao sincronizar com o repositório remoto — publique manualmente."
        print(f"❌ {erro}\n{rebase.stderr}")
        return {"ok": False, "erro": erro}

    git("add", "newsletters.html", f"newsletters/{data_arquivo}.html")

    commit = git(
        "-c", "user.name=Go de Plantão Bot",
        "-c", "user.email=bot@godeplantao.com",
        "commit", "-m", f"Auto: Newsletter semanal ({data_arquivo})",
    )
    if commit.returncode != 0 and "nothing to commit" not in commit.stdout:
        erro = "Falha ao commitar a newsletter."
        print(f"❌ {erro}\n{commit.stderr}")
        return {"ok": False, "erro": erro}

    push = git("push", "origin", "main")
    if push.returncode != 0:
        erro = "Falha ao enviar (push) a newsletter para o repositório."
        print(f"❌ {erro}\n{push.stderr}")
        return {"ok": False, "erro": erro}

    print(f"✅ Newsletter publicada no blog: newsletters/{data_arquivo}.html")
    return {"ok": True}
