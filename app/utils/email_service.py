import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_REMETENTE = os.environ.get("EMAIL_REMETENTE", "")
SENHA_APP_GMAIL = os.environ.get("SENHA_APP_GMAIL", "")


def enviar_email_cancelamento(destinatario, nome_cliente, data_evento, tipo_evento):
    assunto = f"Cancelamento de Reserva - Sabor & Clic ({data_evento})"
    corpo = f"""Olá, {nome_cliente}!

Informamos que a sua reserva da cozinha para '{tipo_evento}' na data {data_evento} foi cancelada pela nossa equipe administrativa.

A data encontra-se novamente disponível em nossa agenda caso deseje reagendar ou entrar em contato conosco.

Atenciosamente,
Equipe Sabor & Clic
"""
    if not EMAIL_REMETENTE or not SENHA_APP_GMAIL:
        print(f"\n[SIMULAÇÃO DE E-MAIL PARA: {destinatario}]\nAssunto: {assunto}\n{corpo}\n")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False