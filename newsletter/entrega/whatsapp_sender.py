"""
Envio da newsletter pelo WhatsApp.

Suporta duas integrações:
  • Z-API  (https://z-api.io)         — configure ZAPI_* no .env
  • Evolution API (self-hosted)        — configure EVOLUTION_* no .env

Escolha automática: usa Z-API se ZAPI_INSTANCE_ID estiver preenchido,
senão tenta Evolution API.
"""

import time
import requests

from config import (
    ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN, ZAPI_NUMEROS,
    EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE, EVOLUTION_NUMEROS,
)

# Limite de caracteres por mensagem WhatsApp
WA_MAX_CHARS = 4000


def enviar_whatsapp(texto: str, numeros=None) -> dict:
    """
    Envia o texto da newsletter pelo WhatsApp.
    Divide automaticamente se o texto exceder 4.000 caracteres.
    """
    if ZAPI_INSTANCE_ID:
        return _enviar_via_zapi(texto, numeros or ZAPI_NUMEROS)
    elif EVOLUTION_API_URL:
        return _enviar_via_evolution(texto, numeros or EVOLUTION_NUMEROS)
    else:
        return {"ok": False, "erro": "Nenhuma integração WhatsApp configurada no .env."}


# ── Z-API ────────────────────────────────────────────────────────────────────

def _enviar_via_zapi(texto: str, numeros) -> dict:
    if not numeros:
        return {"ok": False, "erro": "ZAPI_NUMEROS não configurado."}

    base_url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    headers  = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN,
    }

    enviados, erros = [], []
    partes = _dividir_texto(texto)

    for numero in numeros:
        for i, parte in enumerate(partes):
            payload = {"phone": numero, "message": parte}
            try:
                r = requests.post(base_url, json=payload, headers=headers, timeout=20)
                r.raise_for_status()
                if i == 0:
                    enviados.append(numero)
                print(f"WhatsApp Z-API ✅ {numero} (parte {i+1}/{len(partes)})")
                time.sleep(1.5)  # evita ban por spam
            except Exception as e:
                erros.append({"numero": numero, "erro": str(e)})
                print(f"WhatsApp Z-API ❌ {numero}: {e}")
                break

    return {"ok": len(enviados) > 0, "enviados": enviados, "erros": erros, "via": "z-api"}


# ── Evolution API ─────────────────────────────────────────────────────────────

def _enviar_via_evolution(texto: str, numeros) -> dict:
    if not EVOLUTION_API_URL or not numeros:
        return {"ok": False, "erro": "EVOLUTION_API_URL ou EVOLUTION_NUMEROS não configurados."}

    url     = f"{EVOLUTION_API_URL.rstrip('/')}/message/sendText/{EVOLUTION_INSTANCE}"
    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY,
    }

    enviados, erros = [], []
    partes = _dividir_texto(texto)

    for numero in numeros:
        for i, parte in enumerate(partes):
            payload = {
                "number":  numero,
                "options": {"delay": 1200, "presence": "composing"},
                "textMessage": {"text": parte},
            }
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=20)
                r.raise_for_status()
                if i == 0:
                    enviados.append(numero)
                print(f"WhatsApp Evolution ✅ {numero} (parte {i+1}/{len(partes)})")
                time.sleep(2)
            except Exception as e:
                erros.append({"numero": numero, "erro": str(e)})
                print(f"WhatsApp Evolution ❌ {numero}: {e}")
                break

    return {"ok": len(enviados) > 0, "enviados": enviados, "erros": erros, "via": "evolution"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dividir_texto(texto: str) -> list[str]:
    """Divide mensagem em partes se exceder WA_MAX_CHARS, quebrando em linhas."""
    if len(texto) <= WA_MAX_CHARS:
        return [texto]

    partes, atual = [], []
    tamanho = 0
    for linha in texto.split("\n"):
        if tamanho + len(linha) + 1 > WA_MAX_CHARS and atual:
            partes.append("\n".join(atual))
            atual  = [linha]
            tamanho = len(linha)
        else:
            atual.append(linha)
            tamanho += len(linha) + 1

    if atual:
        partes.append("\n".join(atual))
    return partes
