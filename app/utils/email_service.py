import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_REMETENTE = "c.mercon@aluno.ifsp.edu.br"       # Coloque seu Gmail aqui se quiser disparo real
SENHA_APP_GMAIL = "tcqd ohkv qtsn qqvq"       # Coloque a Senha de App de 16 letras aqui

def enviar_email_cancelamento(destinatario, nome_cliente, data_evento, tipo_evento):
    assunto = f"Cancelamento de Reserva - Doce Celebração ({data_evento})"
    corpo = f"""Olá, {nome_cliente}!

Informamos que a sua reserva de buffet para o evento '{tipo_evento}' na data {data_evento} foi cancelada pela nossa equipe administrativa.

A data encontra-se novamente disponível em nossa agenda caso deseje reagendar ou entrar em contato conosco.

Atenciosamente,
Equipe Doce Celebração — Sabor & Clic
"""
    if not EMAIL_REMETENTE or not SENHA_APP_GMAIL:
        print(f"\n[SIMULAÇÃO DE E-MAIL ENVIADO PARA: {destinatario}]\nAssunto: {assunto}\n{corpo}\n")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_REMETENTE, SENHA_APP_GMAIL)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False