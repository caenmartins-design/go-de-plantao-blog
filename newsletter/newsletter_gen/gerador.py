"""Gera o HTML da newsletter e a versão texto para WhatsApp."""

from datetime import datetime, timedelta
from pathlib import Path

from config import BLOG_URL, NEWSLETTERS_DIR

# Paleta GO de Plantão
MAGENTA     = "#bf1668"
MAGENTA_DRK = "#9a1052"
AZUL        = "#3a78b2"
AZUL_DRK    = "#1d3f6c"
TINTA       = "#414145"
PAPEL       = "#e7e7e4"
WHITE       = "#ffffff"
GRAY_50     = "#f8f9fa"
GRAY_200    = "#e2e6ea"

ICONE_CATEGORIA = {
    "Obstetrícia":           "🤱",
    "Ginecologia":           "🔬",
    "Oncologia Ginecológica":"🎗️",
    "Medicina Fetal":        "👶",
    "Climatério":            "🌸",
    "Contracepção":          "💊",
    "Saúde Pública":         "🏥",
}

ICONE_TIPO = {
    "artigo_cientifico": "📄",
    "diretriz":          "📋",
    "noticia":           "📰",
    "evento":            "📅",
}


def gerar_newsletter(artigos_curados: list[dict]) -> dict:
    """
    Gera HTML e texto WhatsApp da newsletter.
    Retorna dict com chaves: html, texto_whatsapp, caminho_html
    """
    if not artigos_curados:
        raise ValueError("Nenhum artigo para gerar a newsletter.")

    agora        = datetime.now()
    data_ini     = (agora - timedelta(days=7)).strftime("%d/%m")
    data_fim     = agora.strftime("%d/%m/%Y")
    semana_label = f"{data_ini} a {data_fim}"

    destaque = next((a for a in artigos_curados if a.get("destaque")), artigos_curados[0])
    demais   = [a for a in artigos_curados if a.get("id") != destaque.get("id")]

    html             = _gerar_html(destaque, demais, semana_label, agora)
    texto_whatsapp   = _gerar_texto_whatsapp(destaque, demais, semana_label)
    caminho          = _salvar_html(html, agora)

    return {
        "html":            html,
        "texto_whatsapp":  texto_whatsapp,
        "caminho_html":    str(caminho),
        "semana":          semana_label,
    }


# ── Gerador HTML ─────────────────────────────────────────────────────────────

def _gerar_html(destaque: dict, demais: list[dict], semana: str, agora: datetime) -> str:
    cards_demais = "\n".join(_card_artigo(a) for a in demais)

    # Agrupa por tipo
    artigos_cient = [a for a in demais if a.get("tipo") == "artigo_cientifico"]
    diretrizes    = [a for a in demais if a.get("tipo") == "diretriz"]
    noticias      = [a for a in demais if a.get("tipo") == "noticia"]
    eventos       = [a for a in demais if a.get("tipo") == "evento"]

    secoes = ""
    if artigos_cient:
        secoes += _secao("📄 Artigos Científicos", artigos_cient)
    if diretrizes:
        secoes += _secao("📋 Novas Diretrizes", diretrizes)
    if noticias:
        secoes += _secao("📰 Notícias e Atualizações", noticias)
    if eventos:
        secoes += _secao("📅 Eventos e Congressos", eventos)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GO de Plantão — Newsletter {semana}</title>
</head>
<body style="margin:0;padding:0;background-color:{PAPEL};font-family:Arial,Helvetica,sans-serif;">

<!-- Wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background-color:{PAPEL};padding:24px 0;">
<tr><td align="center">

<!-- Container -->
<table width="640" cellpadding="0" cellspacing="0" border="0"
       style="max-width:640px;width:100%;background-color:{WHITE};
              border-radius:12px;overflow:hidden;
              box-shadow:0 4px 20px rgba(0,0,0,0.10);">

  <!-- ── HEADER ─────────────────────────────────────────── -->
  <tr>
    <td style="background:linear-gradient(135deg,{MAGENTA} 0%,{MAGENTA_DRK} 50%,{AZUL_DRK} 100%);
               padding:36px 32px 28px;text-align:center;">
      <p style="margin:0 0 4px;font-size:11px;letter-spacing:3px;
                color:rgba(255,255,255,0.7);text-transform:uppercase;">Newsletter Semanal</p>
      <h1 style="margin:0;font-size:32px;font-weight:900;color:{WHITE};
                 letter-spacing:-0.5px;line-height:1.1;">
        GO de Plantão
      </h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.8);">
        Ginecologia &amp; Obstetrícia em dia
      </p>
      <table width="100%" cellpadding="0" cellspacing="0" border="0"
             style="margin-top:20px;">
        <tr>
          <td align="center">
            <span style="display:inline-block;background:rgba(255,255,255,0.15);
                         border-radius:20px;padding:6px 18px;
                         font-size:12px;color:{WHITE};">
              📅 Semana de {semana}
            </span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ── DESTAQUE DA SEMANA ─────────────────────────────── -->
  <tr>
    <td style="padding:0 24px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0"
             style="margin-top:-1px;background:{MAGENTA};border-radius:0 0 8px 8px;
                    padding:6px 16px;text-align:center;">
        <tr>
          <td>
            <span style="font-size:11px;letter-spacing:2px;color:{WHITE};
                         text-transform:uppercase;font-weight:bold;">
              ✨ Destaque da Semana
            </span>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="padding:16px 24px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0"
             style="background:linear-gradient(135deg,{AZUL_DRK},#2a5288);
                    border-radius:10px;overflow:hidden;">
        <tr>
          <td style="padding:28px;">
            <p style="margin:0 0 8px;font-size:11px;color:rgba(255,255,255,0.6);
                       letter-spacing:1px;text-transform:uppercase;">
              {ICONE_CATEGORIA.get(destaque.get('categoria',''), '🔬')}
              {destaque.get('categoria','Ginecologia')} &nbsp;·&nbsp;
              {destaque.get('fonte','')}
            </p>
            <h2 style="margin:0 0 16px;font-size:22px;color:{WHITE};line-height:1.3;">
              {destaque.get('titulo_pt', destaque.get('titulo',''))}
            </h2>
            <p style="margin:0 0 20px;font-size:14px;color:rgba(255,255,255,0.85);
                       line-height:1.7;">
              {_resumo_curto(destaque.get('resumo',''), 350)}
            </p>
            <!-- Ponto-chave -->
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background:rgba(255,255,255,0.12);border-radius:8px;
                           border-left:4px solid rgba(255,255,255,0.5);margin-bottom:20px;">
              <tr>
                <td style="padding:12px 16px;">
                  <p style="margin:0 0 4px;font-size:10px;color:rgba(255,255,255,0.6);
                             text-transform:uppercase;letter-spacing:1px;">Ponto-chave</p>
                  <p style="margin:0;font-size:14px;color:{WHITE};font-weight:bold;
                             line-height:1.5;">
                    {destaque.get('ponto_chave','')}
                  </p>
                </td>
              </tr>
            </table>
            <a href="{destaque.get('url','#')}" target="_blank"
               style="display:inline-block;background:{MAGENTA};color:{WHITE};
                       text-decoration:none;padding:10px 22px;border-radius:6px;
                       font-size:13px;font-weight:bold;">
              Ler artigo completo →
            </a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ── SEÇÕES POR TIPO ────────────────────────────────── -->
  {secoes}

  <!-- ── RODAPÉ ─────────────────────────────────────────── -->
  <tr>
    <td style="background:{AZUL_DRK};padding:28px 32px;text-align:center;">
      <p style="margin:0 0 8px;font-size:16px;font-weight:bold;color:{WHITE};">
        GO de Plantão
      </p>
      <p style="margin:0 0 16px;font-size:12px;color:rgba(255,255,255,0.65);
                line-height:1.6;">
        Curadoria semanal em Ginecologia &amp; Obstetrícia<br>
        Conteúdo educacional para médicos e estudantes
      </p>
      <a href="{BLOG_URL}" target="_blank"
         style="display:inline-block;color:{WHITE};font-size:12px;
                text-decoration:underline;margin-bottom:16px;">
        Acesse o blog completo →
      </a>
      <p style="margin:0;font-size:10px;color:rgba(255,255,255,0.4);line-height:1.5;">
        Esta newsletter tem finalidade exclusivamente educacional.<br>
        Os resumos são gerados com auxílio de IA e revisados por médico.<br>
        Sempre consulte as fontes originais para decisões clínicas.
      </p>
    </td>
  </tr>

</table>
<!-- /Container -->

</td></tr>
</table>
<!-- /Wrapper -->

</body>
</html>"""


def _secao(titulo: str, artigos: list[dict]) -> str:
    cards = "\n".join(_card_artigo(a) for a in artigos)
    return f"""
  <tr>
    <td style="padding:8px 24px 0;">
      <table width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
          <td style="padding:16px 0 12px;border-top:2px solid {GRAY_200};">
            <h3 style="margin:0;font-size:14px;font-weight:bold;color:{TINTA};
                        text-transform:uppercase;letter-spacing:1px;">
              {titulo}
            </h3>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="padding:0 24px 8px;">
      {cards}
    </td>
  </tr>"""


def _card_artigo(a: dict) -> str:
    icone_cat  = ICONE_CATEGORIA.get(a.get("categoria", ""), "🔬")
    icone_tipo = ICONE_TIPO.get(a.get("tipo", ""), "📄")
    por_que    = a.get("por_que_importa", "")

    return f"""
      <table width="100%" cellpadding="0" cellspacing="0" border="0"
             style="margin-bottom:16px;background:{GRAY_50};border-radius:8px;
                    border:1px solid {GRAY_200};overflow:hidden;">
        <tr>
          <td style="padding:18px 20px;">
            <p style="margin:0 0 6px;font-size:11px;color:#888;letter-spacing:0.5px;">
              {icone_tipo} {a.get('tipo','').replace('_',' ').title()} &nbsp;·&nbsp;
              {icone_cat} {a.get('categoria','')} &nbsp;·&nbsp;
              {a.get('fonte','')}
            </p>
            <h4 style="margin:0 0 10px;font-size:16px;color:{TINTA};line-height:1.4;">
              {a.get('titulo_pt', a.get('titulo',''))}
            </h4>
            <p style="margin:0 0 12px;font-size:13px;color:#555;line-height:1.65;">
              {_resumo_curto(a.get('resumo',''), 280)}
            </p>
            {"" if not por_que else f'''
            <table width="100%" cellpadding="0" cellspacing="0" border="0"
                   style="background:{AZUL}15;border-left:3px solid {AZUL};
                           border-radius:0 6px 6px 0;margin-bottom:12px;">
              <tr>
                <td style="padding:8px 12px;">
                  <p style="margin:0;font-size:12px;color:{AZUL_DRK};line-height:1.5;">
                    <strong>Por que importa:</strong> {por_que}
                  </p>
                </td>
              </tr>
            </table>'''}
            <a href="{a.get('url','#')}" target="_blank"
               style="font-size:12px;color:{MAGENTA};font-weight:bold;text-decoration:none;">
              Ler fonte original →
            </a>
          </td>
        </tr>
      </table>"""


def _resumo_curto(texto: str, limite: int) -> str:
    if not texto:
        return ""
    if len(texto) <= limite:
        return texto
    return texto[:limite].rsplit(" ", 1)[0] + "…"


def _salvar_html(html: str, agora: datetime) -> Path:
    nome = f"newsletter_{agora.strftime('%Y-%m-%d')}.html"
    caminho = NEWSLETTERS_DIR / nome
    caminho.write_text(html, encoding="utf-8")
    print(f"Newsletter salva: {caminho}")
    return caminho


# ── Gerador Texto WhatsApp ────────────────────────────────────────────────────

def _gerar_texto_whatsapp(destaque: dict, demais: list[dict], semana: str) -> str:
    linhas = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🔵 *GO DE PLANTÃO*",
        f"📅 Semana de {semana}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "✨ *DESTAQUE DA SEMANA*",
        "",
        f"*{destaque.get('titulo_pt', destaque.get('titulo',''))}*",
        f"_{destaque.get('fonte','')}_",
        "",
        _resumo_curto(destaque.get("resumo", ""), 400),
        "",
        f"🎯 *Ponto-chave:* {destaque.get('ponto_chave','')}",
        f"🔗 {destaque.get('url','')}",
    ]

    # Artigos científicos
    art_cient = [a for a in demais if a.get("tipo") == "artigo_cientifico"]
    if art_cient:
        linhas += ["", "━━━━━━━━━━━━━━━━━━━━━━━━━",
                   "📄 *ARTIGOS CIENTÍFICOS*", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        for i, a in enumerate(art_cient, 1):
            linhas += [
                "",
                f"{i}. *{a.get('titulo_pt', a.get('titulo',''))}*",
                f"   _{a.get('fonte','')}_",
                f"   {_resumo_curto(a.get('resumo',''), 200)}",
                f"   🎯 {a.get('ponto_chave','')}",
                f"   🔗 {a.get('url','')}",
            ]

    # Diretrizes
    dirs = [a for a in demais if a.get("tipo") == "diretriz"]
    if dirs:
        linhas += ["", "━━━━━━━━━━━━━━━━━━━━━━━━━",
                   "📋 *NOVAS DIRETRIZES*", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        for i, a in enumerate(dirs, 1):
            linhas += [
                "",
                f"{i}. *{a.get('titulo_pt', a.get('titulo',''))}*",
                f"   _{a.get('fonte','')}_",
                f"   {_resumo_curto(a.get('resumo',''), 200)}",
                f"   🔗 {a.get('url','')}",
            ]

    # Notícias
    nots = [a for a in demais if a.get("tipo") == "noticia"]
    if nots:
        linhas += ["", "━━━━━━━━━━━━━━━━━━━━━━━━━",
                   "📰 *NOTÍCIAS DA SEMANA*", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        for i, a in enumerate(nots, 1):
            linhas += [
                "",
                f"{i}. *{a.get('titulo_pt', a.get('titulo',''))}*",
                f"   _{a.get('fonte','')}_",
                f"   🔗 {a.get('url','')}",
            ]

    linhas += [
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"🌐 Blog completo: {BLOG_URL}",
        "",
        "_Conteúdo educacional para médicos e estudantes._",
        "_Sempre consulte as fontes originais para decisões clínicas._",
        "",
        "*GO de Plantão* 🩺",
    ]

    return "\n".join(linhas)
