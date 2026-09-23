"""Data models: API schemas, routing result and department addresses."""
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from enum import Enum

class Department(str, Enum):
    """Department inboxes the agent can route to."""
    HR = "human-resources@example.com"
    IT = "it@example.com"
    KADRY = "kadry@example.com"
    HELP_DESK = "help-desk@example.com"
    OTHER = "other@example.com"

class MessageRequest(BaseModel):
    """Incoming message to route."""
    email: EmailStr
    message: str = Field(
        min_length=3,
        max_length=5000
    )

class ProcessResponse(BaseModel):
    """API response for a routing request."""
    status: Literal["success", "failure"]

class RoutingResult(BaseModel):
    """Internal outcome of RoutingAgent.process()."""
    recipient: str
    fallback: bool = False
    message: str | None = None
