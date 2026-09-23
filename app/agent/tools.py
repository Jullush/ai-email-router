"""Tools available to the routing agent."""
from langchain.tools import ToolRuntime, tool
from pydantic import BaseModel, ConfigDict

from app.core.logger import get_logger
from app.models.models import Department
from app.services.mail_service import MailService

log = get_logger(__name__)


class EmailContext(BaseModel):
    """Request data and services injected at runtime, so the LLM can't change them."""
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    sender: str
    message: str
    mail_service: MailService


@tool("send_email", return_direct=True)
def send_email(recipient: Department, runtime: ToolRuntime[EmailContext]) -> str:
    """Forward the incoming message to the selected department."""
    recipient_address = Department(recipient).value
    log.info("Email tool invoked for recipient %s", recipient_address)

    runtime.context.mail_service.send_email(
        recipient=recipient_address,
        sender=runtime.context.sender,
        message=runtime.context.message,
    )
    log.info("Email sent to %s", recipient_address)
    return f"Email successfully sent to {recipient_address}. The routing task is complete."
