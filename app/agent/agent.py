from functools import cache
from typing import Sequence

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_ollama import ChatOllama
from langchain.agents.middleware import ToolCallLimitMiddleware

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import EmailContext, send_email
from app.core.config import settings
from app.core.logger import get_logger
from app.models.models import RoutingResult

log = get_logger(__name__)


def _extract_recipient(messages: Sequence[BaseMessage]) -> str | None:
    """returns the recipient of the first successful send_email call, if any."""
    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    succeeded_ids = {
        m.tool_call_id
        for m in tool_messages
        if m.name == send_email.name and m.status != "error"
    }

    for msg in messages:
        if not isinstance(msg, AIMessage):
            continue
        for call in msg.tool_calls:
            if call["name"] == send_email.name and call["id"] in succeeded_ids:
                return call["args"].get("recipient")

    return None


class RoutingAgent:
    """LLM agent that classifies an email and forwards it to the right department."""

    def __init__(self, llm: BaseChatModel, tools: Sequence[BaseTool], system_prompt: str):
        log.info("Initializing agent...")
        self._agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
            context_schema=EmailContext,
            middleware=[ToolCallLimitMiddleware(tool_name=send_email.name, run_limit=1)]
        )

    def process(self, email: str, message: str) -> RoutingResult:
        """Route a single message; sender and body are passed to the tool outside the LLM."""
        result = self._agent.invoke(
            {"messages": [("user", message)]},
            context=EmailContext(sender=email, message=message),
        )

        recipient = _extract_recipient(result.get("messages", []))

        if not recipient:
            log.warning("LLM did not successfully call the send_email tool")
            return RoutingResult(
                success=False,
                message="Model failed to route email (no successful tool call).",
            )

        return RoutingResult(
            success=True,
            recipient=recipient,
            message=f"Email successfully routed to {recipient}",
        )


@cache
def get_agent() -> RoutingAgent:
    llm = ChatOllama(
        base_url=settings.ollama_host,
        model=settings.model_name,
        temperature=0.0,

    )

    return RoutingAgent(
        llm=llm,
        tools=[send_email],
        system_prompt=SYSTEM_PROMPT,
    )
