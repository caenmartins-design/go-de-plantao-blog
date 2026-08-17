#!/bin/bash
# Automação semanal da newsletter GO de Plantão, rodando localmente via Claude Code.
#
# Substitui o antigo workflow do GitHub Actions e a rotina em nuvem (ambos
# desativados em 2026-08-17): o GH Actions dependia de uma ANTHROPIC_API_KEY
# quebrada, e o ambiente da rotina em nuvem bloqueia acesso a PubMed/CrossRef/
# Google News por política de rede. Rodando aqui, localmente, a curadoria é
# feita pelo próprio Claude Code (sem chave de API externa) e o acesso de rede
# é o mesmo desta máquina, sem bloqueios.
#
# Disparado pelo launchd (br.com.godeplantao.newsletter.plist), toda segunda-feira.
# Para testar manualmente: bash /Users/cae/go-de-plantao-blog/newsletter/automacao_local/rodar.sh

set -euo pipefail

REPO_DIR="/Users/cae/go-de-plantao-blog"
PROMPT_FILE="$REPO_DIR/newsletter/automacao_local/prompt.txt"
CLAUDE_BIN="/Users/cae/.antigravity-ide/extensions/anthropic.claude-code-2.1.231-darwin-arm64/resources/native-binary/claude"

cd "$REPO_DIR"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — iniciando automação local da newsletter ==="

"$CLAUDE_BIN" \
  -p "$(cat "$PROMPT_FILE")" \
  --allowedTools "Bash Read Write Edit Glob Grep" \
  --output-format text

echo "=== $(date '+%Y-%m-%d %H:%M:%S') — automação finalizada ==="
