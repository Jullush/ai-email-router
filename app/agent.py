from functools import cache
from typing import Sequence
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from app.logger import get_logger
from app.tools import send_email
from app.prompts import SYSTEM_PROMPT
from app.config import settings
from app.models import RoutingResult


log = get_logger(__name__)


def _extract_recipient(messages: list) -> str | None:
    #Checker for tool calling
    has_tool_message = any(
        isinstance(m, ToolMessage) and m.name == "send_email"
        for m in messages
    )
    if not has_tool_message:
        return None

    for msg in messages:
        for call in getattr(msg, "tool_calls", []):
            if call.get("name") == "send_email":
                return call.get("args", {}).get("recipient")

    return None


class RoutingAgent:
    def __init__(self, llm: ChatOllama, tools: Sequence[BaseTool], system_prompt: str):
        log.info("Initializing agent...")
        self.agent_executor = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
        )

    def process(self, email: str, message: str) -> RoutingResult:
        result = self.agent_executor.invoke({
            "messages": [("user", f"sender: {email}\nmessage: {message}")]
        })

        messages = result.get("messages", [])
        recipient = _extract_recipient(messages)

        if not recipient:
            log.warning(f"LLM did not trigger send_email tool for sender {email}")
            return RoutingResult(
                success=False,
                message="Model failed to route email (no tool was called)."
            )

        return RoutingResult(
            success=True,
            recipient=recipient,
            message=f"Email successfully routed to {recipient}"
        )


@cache
def get_agent() -> RoutingAgent:
    """a single RoutingAgent instance."""
    llm = ChatOllama(
        base_url=settings.ollama_host,
        model=settings.model_name,
        temperature=0.0
    )

    return RoutingAgent(
        llm=llm,
        tools=[send_email],
        system_prompt=SYSTEM_PROMPT,
    )