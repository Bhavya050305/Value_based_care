"""Recommendations, Actions, and Outcomes schemas."""

from pydantic import BaseModel


class EvidenceReference(BaseModel):
    source_type: str  # "metric" | "rule" | "ml_signal" | "rag_doc"
    source_id: str
    description: str


class RecommendationItem(BaseModel):
    id: str
    aco_id: str
    aco_name: str | None = None
    title: str
    description: str
    category: str
    status: str  # "open" | "accepted" | "dismissed"
    impact_score: float
    evidence: list[EvidenceReference] = []


class ActionCreateRequest(BaseModel):
    recommendation_id: str | None = None
    aco_id: str
    title: str
    assigned_to: str | None = None


class ActionItem(BaseModel):
    id: str
    recommendation_id: str | None = None
    aco_id: str
    title: str
    assigned_to: str | None = None
    status: str  # "in_progress" | "completed" | "cancelled"
    created_at: str
    completed_at: str | None = None


class OutcomeImpact(BaseModel):
    id: str | None = None
    action_id: str
    metric_name: str
    pre_action_value: float
    post_action_value: float
    measured_impact: float
    status: str


class ActionUpdateRequest(BaseModel):
    title: str | None = None
    assigned_to: str | None = None
    status: str | None = None


class OutcomeCreateRequest(BaseModel):
    metric_name: str
    pre_action_value: float
    post_action_value: float
    measured_impact: float | None = None

