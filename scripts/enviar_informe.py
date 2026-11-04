"""Envía por correo el informe semanal de Search Console (solo biblioteca estándar).

Lee GMAIL_USER, GMAIL_APP_PASSWORD y GMAIL_DESTINO de variables de entorno.
Si falta alguna o no hay informe, avisa y sale con código 0. No registra
contraseña, remitente ni destinatario.
"""
import os
import smtplib
import ssl
import sys
from datetime import date
from email.message import EmailMessage
from pathlib import Path

INFORME = Path("informe/informe-gsc.md")
VARIABLES = ("GMAIL_USER", "GMAIL_APP_PASSWORD", "GMAIL_DESTINO")


def main() -> int:
    if not INFORME.is_file():
        print("No hay informe; no se envía correo.")
        return 0

    valores = {v: os.environ.get(v, "").strip() for v in VARIABLES}
    faltan = [v for v, val in valores.items() if not val]
    if faltan:
        print(f"Faltan variables de entorno ({len(faltan)}); no se envía correo.")
        return 0

    msg = EmailMessage()
    msg["Subject"] = f"[Informe GSC] {date.today():%Y-%m-%d}"
    msg["From"] = valores["GMAIL_USER"]
    msg["To"] = valores["GMAIL_DESTINO"]
    msg.set_content(INFORME.read_text(encoding="utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30) as smtp:
            smtp.login(valores["GMAIL_USER"], valores["GMAIL_APP_PASSWORD"])
            smtp.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        # Solo el tipo de error: el texto podría incluir datos de la cuenta.
        print(f"No se pudo enviar el correo ({type(e).__name__}).")
        return 1

    print("Correo enviado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
