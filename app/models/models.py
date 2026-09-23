from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from enum import Enum

class Department(str, Enum):
    HR = "human-resources@example.com"
    IT = "it@example.com"
    KADRY = "kadry@example.com"
    HELP_DESK = "help-desk@example.com"
    OTHER = "other@example.com"

class MessageRequest(BaseModel):
    email: EmailStr
    message: str = Field(
        min_length=3,
        max_length=5000
    )

class ProcessResponse(BaseModel):
    status: Literal["success", "failure"]

class RoutingResult(BaseModel):
    success: bool
    recipient: str | None = None
    message: str | None = None
