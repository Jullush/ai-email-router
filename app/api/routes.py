from fastapi import APIRouter, Depends, HTTPException, status
from app.agent.agent import get_agent, RoutingAgent
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
    log.info(f"Received message routing request from: {request.email}")

    try:
        result: RoutingResult = agent.process(
            email=request.email,
            message=request.message
        )

        if not result.success:
            log.warning(f"Routing failed for {request.email}: {result.message}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=result.message or "Agent could not route the message."
            )

        log.info(f"Successfully routed request from {request.email} to {result.recipient}")
        return ProcessResponse(status="success")

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Unexpected error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to route email request."
        )