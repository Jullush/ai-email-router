import smtplib
from email.message import EmailMessage
from app.core.config import settings

class MailService:
    def send_email(
            self,
            recipient:str,
            sender: str,
            message: str,
    )-> None:
        email = EmailMessage()

        email.set_content(message)
        email["From"] = settings.sender_email
        email["To"] = recipient
        email["Reply-To"] = sender
        email["Subject"] = "Reply-To"
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10.0) as server:
            server.send_message(email)