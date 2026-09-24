"""Data models: API schemas, routing result and department addresses."""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Department(str, Enum):
    """Department inboxes the agent can route to."""
    HR = "human-resources@example.com"
    IT = "it@example.com"
    KADRY = "kadry@example.com"
    HELP_DESK = "help-desk@example.com"
    OTHER = "other@example.com"

class MessageRequest(BaseModel):
    """Incoming message to route."""
    email: EmailStr = Field(description="Sender email address for Reply-To", examples=["user@example.com"])
    subject: str = Field(description="Subject of the message, used in the forwarded email", examples=["Laptop does not boot up"])
    message: str = Field(
        min_length=3,
        max_length=5000,
        description="Customer message content to be classified and routed",
        examples=["My laptop does not boot up after the recent update."],
    )


class ProcessResponse(BaseModel):
    """API response for a routing request."""
    status: Literal["success", "failure"]
    routed_to: EmailStr | None = Field(
        default=None,
        description="Inbox the message was delivered to (the fallback inbox if it could not be classified)",
    )


class RoutingResult(BaseModel):
    """Internal outcome of RoutingAgent.process()."""
    recipient: EmailStr
    fallback: bool = False
    message: str | None = None