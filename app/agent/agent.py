"""LLM routing agent: builds the LangChain agent and interprets its result."""
from functools import cache
from typing import Sequence
import httpx

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
from app.models.models import RoutingResult, Department
from app.services.mail_service import MailService
from ollama import ResponseError as OllamaResponseError

log = get_logger(__name__)


class LLMUnavailableError(Exception):
    """Raised when the LLM could not be reached or failed (for example: Ollama down or timed out)."""


def _extract_recipient(messages: Sequence[BaseMessage]) -> str | None:
    """Return the recipient of the first successful send_email call, if any.

    A call counts as successful only if its matching ToolMessage (linked by
    tool_call_id) has no error status, so failed sends are never reported as routed.
    """
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

    def __init__(
            self,
            llm: BaseChatModel,
            tools: Sequence[BaseTool],
            system_prompt: str,
            mail_service: MailService,
    ):
        """Build the agent graph.

        Args:
            llm: Chat model used for classification.
            tools: Tools the model may call (expected to include send_email).
            system_prompt: Routing rules given to the model.
            mail_service: Used to deliver the message to the fallback inbox.
        """
        log.info("Initializing agent...")
        self._mail_service = mail_service
        self._agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt,
            context_schema=EmailContext,
            middleware=[ToolCallLimitMiddleware(tool_name=send_email.name, run_limit=1)]
        )

    def process(self, email: str, message: str, subject:str) -> RoutingResult:
        """Route a single message to a department.

        The LLM only sees the message body and picks the department; the sender,
        subject and original body are passed to the tool via runtime context, so
        they are forwarded unchanged.

        If the model fails to pick a valid department, the message is forwarded to
        the fallback inbox (Department.OTHER). Infrastructure failures (LLM or SMTP
        unavailable) send nothing and raise, so the client can retry later.

        Args:
            email: Sender address, used as Reply-To.
            message: Message body to classify and forward.
            subject: Subject of the message, used in the forwarded email (not
                shown to the LLM).

        Returns:
            RoutingResult with the inbox the message was sent to; ``fallback`` is
            True if it went to the fallback inbox.

        Raises:
            LLMUnavailableError: if Ollama could not be reached, timed out or
                returned an error; nothing was sent.
            MailDeliveryError: if the message could not be delivered over SMTP,
                either by the tool or on the fallback path.
        """

        _LLM_INFRA_ERRORS = (
            httpx.TransportError,
            ConnectionError,
            OllamaResponseError,
        )

        try:
            result = self._agent.invoke(
                {"messages": [("user", message)]},
                context=EmailContext(sender=email, message=message, subject=subject, mail_service=self._mail_service),
            )
        except _LLM_INFRA_ERRORS as e:
            raise LLMUnavailableError("LLM invocation failed") from e

        recipient = _extract_recipient(result.get("messages", []))

        if recipient:
            return RoutingResult(
                recipient=recipient,
                message=f"Email successfully routed to {recipient}",
            )

        recipient = Department.OTHER.value
        log.warning("Agent did not route the message, falling back to %s", recipient)
        self._mail_service.send_email(recipient=recipient, sender=email, message=message, subject=subject)

        return RoutingResult(
            recipient=recipient,
            fallback=True,
            message=f"Email could not be classified, sent to fallback inbox {recipient}",
        )


@cache
def get_agent() -> RoutingAgent:
    """Return the shared RoutingAgent, created on first use (FastAPI dependency)."""
    llm = ChatOllama(
        base_url=settings.ollama_host,
        model=settings.model_name,
        temperature=0.0,
        client_kwargs={"timeout": settings.llm_timeout}
    )

    return RoutingAgent(
        llm=llm,
        tools=[send_email],
        system_prompt=SYSTEM_PROMPT,
        mail_service=MailService(),
    )