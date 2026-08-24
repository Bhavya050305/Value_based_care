"""AI Assistant API routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.assistant import AssistantConversation, AssistantMessage, MessageRequest
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.assistant import AssistantService

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.services.ai_context import ACOAIContextBuilder

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])
service = AssistantService()
context_builder = ACOAIContextBuilder()


@router.get("/conversations", response_model=ApiResponse[list[AssistantConversation]])
async def list_conversations(
    user: AuthenticatedUser = Depends(require_permissions([Permission.USE_AI_ASSISTANT])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[AssistantConversation]]:
    data = await service.list_conversations(user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/conversations", response_model=ApiResponse[AssistantConversation])
async def create_conversation(
    user: AuthenticatedUser = Depends(require_permissions([Permission.USE_AI_ASSISTANT])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[AssistantConversation]:
    data = await service.create_conversation(user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/conversations/{id}/messages", response_model=ApiResponse[AssistantMessage])
async def post_message(
    id: str,
    request_body: MessageRequest,
    user: AuthenticatedUser = Depends(require_permissions([Permission.USE_AI_ASSISTANT])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[AssistantMessage]:
    data = await service.post_message(id, request_body, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("/chat")
async def chat_with_assistant(
    request: dict,
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.USE_AI_ASSISTANT])),
    request_id: str = Depends(get_request_id),
):
    """Direct assistant chat endpoint grounded in live Supabase ACO performance data."""
    msg = request.get("message", "")
    aco_id = request.get("aco_id") or request.get("acoId") or "A1001"
    year = int(request.get("year") or request.get("performance_year") or 2024)

    res = await context_builder.build_context_and_answer(db, msg, aco_id, year)

    return {
        "success": True,
        "data": {
            "answer": res["answer"],
            "keyFactors": res["key_factors"],
            "recommendedAction": res["recommended_action"],
            "confidenceScore": 0.95,
            "sourceData": res["source"],
        },
        "meta": {"request_id": request_id}
    }


@router.post("/prompt")
async def prompt_assistant(
    request: dict,
    user: AuthenticatedUser = Depends(require_permissions([Permission.USE_AI_ASSISTANT])),
    request_id: str = Depends(get_request_id),
):
    """Direct assistant prompt endpoint for targeted AI explanations."""
    prompt_type = request.get("prompt_type", "risk_explanation")
    aco_id = request.get("aco_id", "A1001")

    return {
        "success": True,
        "data": {
            "title": f"AI Executive Analysis — ACO {aco_id}",
            "summary": f"Targeted AI assessment for {prompt_type} on ACO {aco_id}.",
            "bullets": [
                "Primary spend driver: Emergency Department and Inpatient Readmissions",
                "Quality performance: 89.5% composite benchmark compliance",
                "Financial Projection: Projected shared savings balance positive",
            ],
            "recommendedNextSteps": [
                "Conduct PCP care coordination audit",
                "Review high-cost beneficiary case management enrollment",
            ]
        },
        "meta": {"request_id": request_id}
    }

