"""HTTP endpoints for message routing."""
from fastapi import APIRouter, Depends, HTTPException, status
from app.agent.agent import get_agent, LLMUnavailableError, RoutingAgent
from app.services.mail_service import MailDeliveryError
from app.models.models import MessageRequest, ProcessResponse
from app.core.logger import get_logger
from app.models.models import RoutingResult

log = get_logger(__name__)
router = APIRouter()

@router.post("/messages", response_model=ProcessResponse)
def process_message(
        request: MessageRequest,
        agent: RoutingAgent = Depends(get_agent)
):
    """Classify a message with the LLM agent and forward it to the matching department.

    Messages the agent cannot classify are sent to the fallback inbox. Returns 503
    (and sends nothing) if the LLM or the SMTP server is unavailable.
    """
    log.info(f"Received message routing request from: {request.email}")

    try:
        result: RoutingResult = agent.process(
            email=request.email,
            message=request.message
        )

        if result.fallback:
            log.warning(f"Request from {request.email} routed to fallback inbox {result.recipient}")
        else:
            log.info(f"Successfully routed request from {request.email} to {result.recipient}")
        return ProcessResponse(status="success")

    except LLMUnavailableError:
        log.error(f"LLM unavailable for {request.email}, nothing sent", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM unavailable")

    except MailDeliveryError:
        log.error(f"Mail server unavailable for {request.email}, nothing sent", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Mail server unavailable")

    except Exception as e:
        log.error(f"Unexpected error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to route email request."
        )