"""Unit tests for AI Assistant conversation service and fallback logic."""

import pytest
from app.schemas.assistant import MessageRequest
from app.services.assistant import AssistantService


@pytest.mark.asyncio
async def test_assistant_service_conversation_lifecycle():
    service = AssistantService()

    convs = await service.list_conversations()
    assert len(convs) >= 1

    new_conv = await service.create_conversation()
    assert new_conv.id.startswith("conv_")

    msg_req = MessageRequest(
        message="What is the projected savings for Florida Sunshine Health ACO?",
    )

    reply = await service.post_message(new_conv.id, msg_req)
    assert reply.role == "assistant"
    assert len(reply.content) > 0
    assert reply.evidence_references is not None
