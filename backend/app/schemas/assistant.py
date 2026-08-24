"""AI Assistant, Reports, and Settings domain schemas."""

from pydantic import BaseModel


class AssistantMessage(BaseModel):
    id: str
    role: str  # "user" | "assistant" | "system"
    content: str
    created_at: str
    evidence_references: list[dict] = []


class AssistantConversation(BaseModel):
    id: str
    title: str
    created_at: str
    messages: list[AssistantMessage] = []


class MessageRequest(BaseModel):
    message: str


class ReportCreateRequest(BaseModel):
    report_type: str  # "executive_summary" | "aco_deep_dive" | "quality_performance"
    aco_id: str | None = None
    performance_year: int | None = None


class ReportItem(BaseModel):
    id: str
    report_type: str
    status: str  # "pending" | "generating" | "completed" | "failed"
    download_url: str | None = None
    created_at: str


class ProfileSettings(BaseModel):
    user_id: str
    full_name: str | None = None
    email: str | None = None
    role: str | None = None


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    email: str | None = None


class UserPreferences(BaseModel):
    theme: str = "dark"
    email_notifications: bool = True
    default_performance_year: int = 2024


class PreferencesUpdateRequest(BaseModel):
    theme: str | None = None
    email_notifications: bool | None = None
    default_performance_year: int | None = None

