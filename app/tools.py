from pydantic import BaseModel, EmailStr
from app.models import Department
from app.services.mail_service import MailService
from langchain_core.tools import tool
from app.logger import get_logger

mail_service = MailService()

log = get_logger(__name__)

class SendEmailInput(BaseModel):
    recipient: Department
    sender: EmailStr
    message: str

@tool("send_email", args_schema=SendEmailInput, return_direct=True)
def send_email(recipient:str,sender:str, message:str)-> None:
    """Sends an email to a specified recipient with a sender and message body.

    The agent stops after this side-effecting tool completes, preventing it from
    issuing another SMTP send while processing the same request.
    """
    log.info(f"Email tool invoked for recipient {recipient}")
    mail_service.send_email(
        recipient=recipient,
        sender=sender,
        message=message,
    )
    log.info(f"Email sent to {recipient}")


