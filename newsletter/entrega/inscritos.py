"""Busca e-mails inscritos via formulário (planilha do Google Forms publicada como CSV)."""

import csv
import io
import re

import requests

from config import NEWSLETTER_SIGNUP_CSV_URL

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def buscar_inscritos() -> list[str]:
    """
    Lê a planilha de respostas do Google Forms (publicada como CSV) e retorna
    a lista de e-mails válidos. Retorna lista vazia se não configurado ou em
    caso de falha de rede — nunca interrompe o envio da newsletter.
    """
    if not NEWSLETTER_SIGNUP_CSV_URL:
        return []

    try:
        resp = requests.get(NEWSLETTER_SIGNUP_CSV_URL, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Falha ao buscar inscritos da planilha: {e}")
        return []

    leitor = csv.DictReader(io.StringIO(resp.text))
    coluna_email = next(
        (c for c in (leitor.fieldnames or []) if c.strip().lower() in ("e-mail", "email")),
        None,
    )
    if not coluna_email:
        print("⚠️  Coluna de e-mail não encontrada na planilha de inscritos.")
        return []

    emails = []
    for linha in leitor:
        email = (linha.get(coluna_email) or "").strip()
        if email and EMAIL_REGEX.match(email):
            emails.append(email)

    return emails
