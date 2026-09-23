"""SMTP delivery of routed messages."""
import smtplib
from email.message import EmailMessage
from app.core.config import settings


class MailDeliveryError(Exception):
    """Raised when a message could not be delivered over SMTP."""


class MailService:
    """Sends routed messages over SMTP."""

    def send_email(
            self,
            recipient:str,
            sender: str,
            message: str,
    )-> None:
        """Forward a message to a department inbox.

        The email is sent from the routing service address, with the original
        sender set as Reply-To so the department can answer them directly.

        Raises:
            MailDeliveryError: if the SMTP server is unreachable or rejects the message.
        """
        email = EmailMessage()

        email.set_content(message)
        email["From"] = settings.sender_email
        email["To"] = recipient
        email["Reply-To"] = sender
        email["Subject"] = f"[Routed] Message from {sender}"
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10.0) as server:
                server.send_message(email)
        except (smtplib.SMTPException, OSError) as e:
            raise MailDeliveryError(f"Failed to deliver message to {recipient}") from e