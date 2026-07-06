#!/usr/bin/env python3
"""
GO de Plantão — Motor de Busca + Newsletter Semanal
====================================================

Uso:
  python main.py buscar          → busca artigos de todas as fontes
  python main.py curar           → curadoria com IA (usa dados da última busca)
  python main.py gerar           → gera HTML e texto WhatsApp da newsletter
  python main.py enviar-email    → envia newsletter por e-mail
  python main.py enviar-whatsapp → envia newsletter por WhatsApp
  python main.py tudo            → executa todo o pipeline de uma vez
  python main.py agendar         → inicia o agendador semanal (roda toda segunda-feira)
  python main.py preview         → abre a última newsletter no navegador
"""

import json
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

# Garante que o diretório do script está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from config         import DADOS_DIR, NEWSLETTERS_DIR
from buscador       import buscar_tudo, marcar_vistos
from curador        import curar_artigos
from newsletter_gen import gerar_newsletter, publicar_no_blog
from entrega        import enviar_email, enviar_whatsapp

ARTIGOS_BRUTOS_FILE  = DADOS_DIR / "artigos_brutos.json"
ARTIGOS_CURADOS_FILE = DADOS_DIR / "artigos_curados.json"
NEWSLETTER_ATUAL     = DADOS_DIR / "newsletter_atual.json"


# ── Etapas do pipeline ────────────────────────────────────────────────────────

def cmd_buscar():
    """Etapa 1 — Busca artigos em todas as fontes."""
    print("\n════════════════════════════════════════════════")
    print("  ETAPA 1 — BUSCA DE ARTIGOS")
    print("════════════════════════════════════════════════")
    artigos = buscar_tudo()
    _salvar_json(ARTIGOS_BRUTOS_FILE, artigos)
    print(f"\n✅ {len(artigos)} artigos salvos em {ARTIGOS_BRUTOS_FILE.name}")
    return artigos


def cmd_curar(artigos_brutos=None):
    """Etapa 2 — Curadoria e sumarização com Claude."""
    print("\n════════════════════════════════════════════════")
    print("  ETAPA 2 — CURADORIA COM IA")
    print("════════════════════════════════════════════════")

    if artigos_brutos is None:
        artigos_brutos = _carregar_json(ARTIGOS_BRUTOS_FILE)
        if not artigos_brutos:
            print("❌ Nenhum artigo bruto encontrado. Execute 'buscar' primeiro.")
            return []

    curados = curar_artigos(artigos_brutos)
    _salvar_json(ARTIGOS_CURADOS_FILE, curados)
    print(f"\n✅ {len(curados)} artigos curados salvos em {ARTIGOS_CURADOS_FILE.name}")
    return curados


def cmd_gerar(artigos_curados=None):
    """Etapa 3 — Gera HTML e texto WhatsApp."""
    print("\n════════════════════════════════════════════════")
    print("  ETAPA 3 — GERAÇÃO DA NEWSLETTER")
    print("════════════════════════════════════════════════")

    if artigos_curados is None:
        artigos_curados = _carregar_json(ARTIGOS_CURADOS_FILE)
        if not artigos_curados:
            print("❌ Nenhum artigo curado. Execute 'curar' primeiro.")
            return None

    resultado = gerar_newsletter(artigos_curados)
    _salvar_json(NEWSLETTER_ATUAL, resultado | {"artigos": artigos_curados})
    print(f"\n✅ Newsletter gerada: {resultado['caminho_html']}")
    print(f"   Semana: {resultado['semana']}")

    print("\n════════════════════════════════════════════════")
    print("  ETAPA 3b — PUBLICAÇÃO NA ABA NEWSLETTERS DO BLOG")
    print("════════════════════════════════════════════════")
    publicar_no_blog(resultado, artigos_curados)

    return resultado


def cmd_enviar_email(resultado=None):
    """Etapa 4a — Envia newsletter por e-mail."""
    print("\n════════════════════════════════════════════════")
    print("  ETAPA 4a — ENVIO POR E-MAIL")
    print("════════════════════════════════════════════════")

    if resultado is None:
        dados = _carregar_json(NEWSLETTER_ATUAL)
        if not dados:
            print("❌ Nenhuma newsletter gerada. Execute 'gerar' primeiro.")
            return
        resultado = dados

    res = enviar_email(resultado["html"], resultado["semana"])
    if res["ok"]:
        print(f"\n✅ E-mail enviado para {len(res.get('enviados',[]))} destinatário(s).")
    else:
        print(f"\n❌ Erro no envio de e-mail: {res.get('erro','')}")
    for err in res.get("erros", []):
        print(f"   ⚠️  {err['dest']}: {err['erro']}")
    return res


def cmd_enviar_whatsapp(resultado=None):
    """Etapa 4b — Envia newsletter pelo WhatsApp."""
    print("\n════════════════════════════════════════════════")
    print("  ETAPA 4b — ENVIO POR WHATSAPP")
    print("════════════════════════════════════════════════")

    if resultado is None:
        dados = _carregar_json(NEWSLETTER_ATUAL)
        if not dados:
            print("❌ Nenhuma newsletter gerada. Execute 'gerar' primeiro.")
            return
        resultado = dados

    res = enviar_whatsapp(resultado["texto_whatsapp"])
    if res["ok"]:
        print(f"\n✅ WhatsApp enviado para {len(res.get('enviados',[]))} número(s) via {res.get('via','?')}.")
    else:
        print(f"\n❌ Erro no envio WhatsApp: {res.get('erro','')}")
    return res


def cmd_tudo():
    """Pipeline completo: buscar → curar → gerar → enviar."""
    print("\n╔══════════════════════════════════════════════╗")
    print("║   GO DE PLANTÃO — PIPELINE NEWSLETTER SEMANAL  ║")
    print("╚══════════════════════════════════════════════╝")

    artigos_brutos  = cmd_buscar()
    if not artigos_brutos:
        print("⚠️  Nenhum artigo novo encontrado esta semana.")
        return

    artigos_curados = cmd_curar(artigos_brutos)
    if not artigos_curados:
        print("⚠️  Curadoria não retornou artigos.")
        return

    resultado = cmd_gerar(artigos_curados)
    if not resultado:
        return

    cmd_enviar_email(resultado)

    # Marca artigos como vistos para evitar repetição
    marcar_vistos(artigos_brutos)

    print("\n╔══════════════════════════════════════════════╗")
    print("║          ✅ NEWSLETTER ENVIADA COM SUCESSO      ║")
    print("╚══════════════════════════════════════════════╝\n")


def cmd_preview():
    """Abre a última newsletter gerada no navegador."""
    newsletters = sorted(NEWSLETTERS_DIR.glob("newsletter_*.html"))
    if not newsletters:
        print("❌ Nenhuma newsletter encontrada. Execute 'gerar' primeiro.")
        return
    ultima = newsletters[-1]
    print(f"Abrindo: {ultima}")
    webbrowser.open(ultima.as_uri())


def cmd_agendar():
    """Inicia o agendador — executa o pipeline toda segunda-feira às 07:00."""
    import schedule
    import time as _time

    print("\n🕐 Agendador iniciado.")
    print("   Execução automática: toda segunda-feira às 07:00")
    print("   (Pressione Ctrl+C para parar)\n")

    schedule.every().monday.at("07:00").do(cmd_tudo)

    while True:
        schedule.run_pending()
        _time.sleep(60)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _salvar_json(caminho: Path, dados):
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def _carregar_json(caminho: Path):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return []


# ── Entry point ───────────────────────────────────────────────────────────────

COMANDOS = {
    "buscar":           cmd_buscar,
    "curar":            cmd_curar,
    "gerar":            cmd_gerar,
    "enviar-email":     cmd_enviar_email,
    "enviar-whatsapp":  cmd_enviar_whatsapp,
    "tudo":             cmd_tudo,
    "preview":          cmd_preview,
    "agendar":          cmd_agendar,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDOS:
        print(__doc__)
        sys.exit(0)
    COMANDOS[sys.argv[1]]()
