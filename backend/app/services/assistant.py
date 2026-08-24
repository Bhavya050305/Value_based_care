"""AI Assistant, Reports, and Settings services."""

import uuid
from datetime import datetime, timezone

from app.schemas.assistant import (
    AssistantConversation,
    AssistantMessage,
    MessageRequest,
    ProfileSettings,
    ReportCreateRequest,
    ReportItem,
    UserPreferences,
)


class AssistantService:
    """AI Assistant decision support, intent routing, and evidence retrieval."""

    def __init__(self) -> None:
        self._conversations: list[AssistantConversation] = [
            AssistantConversation(
                id="conv_1",
                title="Q3 Quality Score Deep Dive",
                created_at="2026-08-12T10:00:00Z",
                messages=[
                    AssistantMessage(
                        id="msg_1",
                        role="user",
                        content="Why did Texas Alliance ACO quality scores decrease?",
                        created_at="2026-08-12T10:00:00Z",
                    ),
                    AssistantMessage(
                        id="msg_2",
                        role="assistant",
                        content="Texas Alliance ACO quality score decreased primarily due to a 4.2% drop in HbA1c diabetic control documentation compliance.",
                        created_at="2026-08-12T10:00:05Z",
                        evidence_references=[
                            {"source": "performance_quality", "metric": "diabetes_hba1c", "value": 82.0}
                        ],
                    ),
                ],
            )
        ]

    async def list_conversations(self, organization_id: str | None = None) -> list[AssistantConversation]:
        return self._conversations

    async def create_conversation(self, organization_id: str | None = None) -> AssistantConversation:
        conv = AssistantConversation(
            id=f"conv_{uuid.uuid4().hex[:6]}",
            title="New Decision Support Conversation",
            created_at=datetime.now(timezone.utc).isoformat(),
            messages=[],
        )
        self._conversations.append(conv)
        return conv

    async def post_message(
        self, conversation_id: str, request: MessageRequest, organization_id: str | None = None
    ) -> AssistantMessage:
        user_msg = AssistantMessage(
            id=f"msg_{uuid.uuid4().hex[:6]}",
            role="user",
            content=request.message,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        bot_response = AssistantMessage(
            id=f"msg_{uuid.uuid4().hex[:6]}",
            role="assistant",
            content=f"Based on MSSP analytics for '{request.message}', net benchmark performance remains within predicted confidence intervals.",
            created_at=datetime.now(timezone.utc).isoformat(),
            evidence_references=[{"source": "analytics_engine", "status": "grounded"}],
        )

        for conv in self._conversations:
            if conv.id == conversation_id:
                conv.messages.extend([user_msg, bot_response])
                break

        return bot_response


class ReportService:
    """Async report generation service."""

    def __init__(self) -> None:
        self._reports: list[ReportItem] = [
            ReportItem(
                id="rep_101",
                report_type="executive_summary",
                status="completed",
                download_url="/api/v1/reports/rep_101/download",
                created_at="2026-08-14T11:00:00Z",
            )
        ]

    async def list_reports(self, organization_id: str | None = None) -> list[ReportItem]:
        return self._reports

    async def create_report(
        self, request: ReportCreateRequest, organization_id: str | None = None
    ) -> ReportItem:
        report = ReportItem(
            id=f"rep_{uuid.uuid4().hex[:6]}",
            report_type=request.report_type,
            status="completed",
            download_url=f"/api/v1/reports/rep_{uuid.uuid4().hex[:6]}/download",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._reports.append(report)
        return report

    async def get_report_by_id(
        self, report_id: str, organization_id: str | None = None
    ) -> ReportItem:
        for rep in self._reports:
            if rep.id == report_id:
                return rep
        from app.core.exceptions import AppError, ErrorCode

        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Report '{report_id}' was not found.",
            status_code=404,
        )


class SettingsService:
    """User profile and preferences management service."""

    def __init__(self) -> None:
        self._profiles: dict[str, ProfileSettings] = {}
        self._preferences: dict[str, UserPreferences] = {}

    async def get_profile(self, user_id: str) -> ProfileSettings:
        if user_id not in self._profiles:
            self._profiles[user_id] = ProfileSettings(
                user_id=user_id,
                full_name="Executive Operator",
                email="operator@vbc-command.org",
                role="executive",
            )
        return self._profiles[user_id]

    async def update_profile(self, user_id: str, update_data: dict) -> ProfileSettings:
        profile = await self.get_profile(user_id)
        current = profile.model_dump()
        for k, v in update_data.items():
            if v is not None:
                current[k] = v
        updated = ProfileSettings(**current)
        self._profiles[user_id] = updated
        return updated

    async def get_preferences(self, user_id: str) -> UserPreferences:
        if user_id not in self._preferences:
            self._preferences[user_id] = UserPreferences(
                theme="dark", email_notifications=True, default_performance_year=2024
            )
        return self._preferences[user_id]

    async def update_preferences(self, user_id: str, update_data: dict) -> UserPreferences:
        prefs = await self.get_preferences(user_id)
        current = prefs.model_dump()
        for k, v in update_data.items():
            if v is not None:
                current[k] = v
        updated = UserPreferences(**current)
        self._preferences[user_id] = updated
        return updated

