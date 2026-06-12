# src/sender.py

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_ADDRESS      = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send(subject: str, html: str) -> None:
    # on lit les variables ICI, pas au moment de l'import
    recipient_emails = [
        e.strip()
        for e in os.getenv("RECIPIENT_EMAILS", "").split(",")
        if e.strip()
    ]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = ", ".join(recipient_emails)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, recipient_emails, msg.as_string())
        print(f"[sender] sent to {recipient_emails}")