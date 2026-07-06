"""Envio da newsletter por e-mail via SMTP (Gmail, Outlook, etc.)."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime

from config import (
    EMAIL_SMTP_HOST, EMAIL_SMTP_PORT,
    EMAIL_REMETENTE, EMAIL_SENHA,
    EMAIL_NOME_REMETENTE, EMAIL_ASSUNTO,
    EMAIL_DESTINATARIOS,
)


def enviar_email(html: str, semana: str, destinatarios=None) -> dict:
    """
    Envia a newsletter HTML por e-mail.

    Parâmetros
    ----------
    html           : Conteúdo HTML da newsletter
    semana         : String "DD/MM a DD/MM/YYYY" para o assunto
    destinatarios  : Lista de e-mails; usa EMAIL_DESTINATARIOS do .env se omitido

    Retorna dict com ok=True/False e detalhes
    """
    destinos = destinatarios or EMAIL_DESTINATARIOS
    if not destinos:
        return {"ok": False, "erro": "Nenhum destinatário configurado."}

    if not EMAIL_REMETENTE or not EMAIL_SENHA:
        return {"ok": False, "erro": "EMAIL_REMETENTE ou EMAIL_SENHA não configurados."}

    assunto = f"{EMAIL_ASSUNTO} | Semana {semana}"
    enviados = []
    erros    = []

    try:
        # Remove espaços da senha de app do Google (formato xxxx xxxx xxxx xxxx)
        senha = EMAIL_SENHA.replace(" ", "")
        with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_REMETENTE, senha)

            for dest in destinos:
                try:
                    msg = _construir_mensagem(dest, assunto, html)
                    smtp.sendmail(EMAIL_REMETENTE, dest, msg.as_string())
                    enviados.append(dest)
                    print(f"E-mail ✅ enviado para {dest}")
                except Exception as e:
                    erros.append({"dest": dest, "erro": str(e)})
                    print(f"E-mail ❌ erro para {dest}: {e}")

    except smtplib.SMTPAuthenticationError:
        return {
            "ok": False,
            "erro": "Falha de autenticação SMTP. Verifique EMAIL_REMETENTE e EMAIL_SENHA no .env."
        }
    except Exception as e:
        return {"ok": False, "erro": f"Erro de conexão SMTP: {e}"}

    return {
        "ok":      len(enviados) > 0,
        "enviados": enviados,
        "erros":    erros,
        "total":    len(destinos),
    }


def _construir_mensagem(destinatario: str, assunto: str, html: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"]    = formataddr((EMAIL_NOME_REMETENTE, EMAIL_REMETENTE))
    msg["To"]      = destinatario

    # Parte texto simples (fallback)
    texto_simples = (
        "Este e-mail requer um cliente de e-mail com suporte a HTML.\n"
        "Acesse a newsletter em seu navegador."
    )
    msg.attach(MIMEText(texto_simples, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg
