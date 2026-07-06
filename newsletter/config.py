import os
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).parent / ".env"

# Lê a chave diretamente do .env para garantir que a do usuário tem prioridade
# (o ambiente do Claude Code injeta uma chave própria que não funciona externamente)
def _ler_do_env(chave: str) -> str:
    if _env_path.exists():
        for linha in _env_path.read_text().splitlines():
            if linha.startswith(f"{chave}=") and not linha.startswith("#"):
                return linha.split("=", 1)[1].strip()
    return ""

load_dotenv(_env_path, override=True)

BASE_DIR        = Path(__file__).parent
DADOS_DIR       = BASE_DIR / "dados"
NEWSLETTERS_DIR = DADOS_DIR / "newsletters"
VISTOS_FILE     = DADOS_DIR / "vistos.json"

DADOS_DIR.mkdir(exist_ok=True)
NEWSLETTERS_DIR.mkdir(exist_ok=True)

# Claude — lê diretamente do .env para evitar conflito com chave do Claude Code
ANTHROPIC_API_KEY = _ler_do_env("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")

# Email
EMAIL_SMTP_HOST       = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT       = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_REMETENTE       = os.getenv("EMAIL_REMETENTE", "")
EMAIL_SENHA           = os.getenv("EMAIL_SENHA", "")
EMAIL_NOME_REMETENTE  = os.getenv("EMAIL_NOME_REMETENTE", "GO de Plantão Newsletter")
EMAIL_ASSUNTO         = os.getenv("EMAIL_ASSUNTO", "GO de Plantão | Atualização Semanal em GO")
EMAIL_DESTINATARIOS   = [e.strip() for e in os.getenv("EMAIL_DESTINATARIOS", "").split(",") if e.strip()]

# WhatsApp — Z-API
ZAPI_INSTANCE_ID  = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN        = os.getenv("ZAPI_TOKEN", "")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")
ZAPI_NUMEROS      = [n.strip() for n in os.getenv("ZAPI_NUMEROS", "").split(",") if n.strip()]

# WhatsApp — Evolution API
EVOLUTION_API_URL  = os.getenv("EVOLUTION_API_URL", "")
EVOLUTION_API_KEY  = os.getenv("EVOLUTION_API_KEY", "")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "go-plantao")
EVOLUTION_NUMEROS  = [n.strip() for n in os.getenv("EVOLUTION_NUMEROS", "").split(",") if n.strip()]

# Busca
DIAS_RETROATIVOS = int(os.getenv("DIAS_RETROATIVOS", "7"))
MAX_POR_FONTE    = int(os.getenv("MAX_POR_FONTE", "20"))
MAX_NEWSLETTER   = int(os.getenv("MAX_NEWSLETTER", "10"))

# Blog
BLOG_URL = os.getenv("BLOG_URL", "https://godeplantao.cae-nmartins.workers.dev/")
