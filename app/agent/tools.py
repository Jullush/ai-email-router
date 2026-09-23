from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict

from app.core.logger import get_logger
from app.models.models import Department
from app.services.mail_service import MailService

mail_service = MailService()

log = get_logger(__name__)


class EmailContext(BaseModel):
    """Request data injected at runtime, so the LLM wouldn't be able to change it."""
    model_config = ConfigDict(frozen=True)
    sender: str
    message: str


@tool("send_email", return_direct=True)
def send_email(recipient: Department, runtime: ToolRuntime[EmailContext]) -> str:
    """Routes the incoming email to the selected dept."""
    recipient_address = Department(recipient).value
    log.info("Email tool invoked for recipient %s", recipient_address)

    mail_service.send_email(
        recipient=recipient_address,
        sender=runtime.context.sender,
        message=runtime.context.message,
    )
    log.info("Email sent to %s", recipient_address)
    return f"Email successfully sent to {recipient_address}. The routing task is complete."
