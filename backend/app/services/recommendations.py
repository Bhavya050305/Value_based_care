"""Recommendations, Actions, and Outcomes business domain services."""

import uuid
from datetime import datetime, timezone

from app.core.exceptions import AppError, ErrorCode
from app.schemas.recommendations import (
    ActionCreateRequest,
    ActionItem,
    EvidenceReference,
    OutcomeImpact,
    RecommendationItem,
)


class RecommendationService:
    """Rules and analytics driven recommendation generator."""

    def __init__(self) -> None:
        self._mock_recs = [
            RecommendationItem(
                id="rec_101",
                aco_id="A1001",
                aco_name="Florida Sunshine Health ACO",
                title="Establish Post-Acute SNF Care Pathways",
                description="Reduce average SNF length of stay by 2.5 days through preferred provider network routing.",
                category="Utilization Management",
                status="open",
                impact_score=8.5,
                evidence=[
                    EvidenceReference(source_type="metric", source_id="snf_los_avg", description="SNF Length of stay average is 24.5 days vs benchmark 21.0 days."),
                    EvidenceReference(source_type="ml_signal", source_id="shap_snf_days", description="SHAP feature attribution identifies SNF days as top expenditure driver."),
                ],
            ),
            RecommendationItem(
                id="rec_102",
                aco_id="A1003",
                aco_name="Texas Alliance ACO",
                title="Expand Diabetic Care Coordination Program",
                description="Enroll high-risk HbA1c > 9% beneficiaries into telephonic nurse navigator program.",
                category="Quality Enhancement",
                status="open",
                impact_score=9.1,
                evidence=[
                    EvidenceReference(source_type="metric", source_id="quality_diabetes_hba1c", description="Diabetes control quality score dropped 4.2 percentage points."),
                ],
            ),
        ]

    async def list_recommendations(
        self, aco_id: str | None = None, organization_id: str | None = None
    ) -> list[RecommendationItem]:
        if aco_id:
            return [r for r in self._mock_recs if r.aco_id == aco_id]
        return self._mock_recs

    async def get_recommendation_by_id(
        self, rec_id: str, organization_id: str | None = None
    ) -> RecommendationItem:
        for rec in self._mock_recs:
            if rec.id == rec_id:
                return rec
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Recommendation '{rec_id}' was not found.",
            status_code=404,
        )

    async def accept_recommendation(
        self, rec_id: str, organization_id: str | None = None
    ) -> RecommendationItem:
        rec = await self.get_recommendation_by_id(rec_id, organization_id)
        return RecommendationItem(**{**rec.model_dump(), "status": "accepted"})

    async def dismiss_recommendation(
        self, rec_id: str, organization_id: str | None = None
    ) -> RecommendationItem:
        rec = await self.get_recommendation_by_id(rec_id, organization_id)
        return RecommendationItem(**{**rec.model_dump(), "status": "dismissed"})


class ActionService:
    """Action tracking and closed-loop execution state machine."""

    def __init__(self) -> None:
        self._actions: list[ActionItem] = [
            ActionItem(
                id="act_501",
                recommendation_id="rec_101",
                aco_id="A1001",
                title="Establish Post-Acute SNF Care Pathways",
                assigned_to="Care Management Director",
                status="in_progress",
                created_at="2026-08-01T09:00:00Z",
            )
        ]

    async def list_actions(
        self, aco_id: str | None = None, organization_id: str | None = None
    ) -> list[ActionItem]:
        if aco_id:
            return [a for a in self._actions if a.aco_id == aco_id]
        return self._actions

    async def create_action(
        self, request: ActionCreateRequest, organization_id: str | None = None
    ) -> ActionItem:
        new_action = ActionItem(
            id=f"act_{uuid.uuid4().hex[:6]}",
            recommendation_id=request.recommendation_id,
            aco_id=request.aco_id,
            title=request.title,
            assigned_to=request.assigned_to or "Unassigned",
            status="in_progress",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._actions.append(new_action)
        return new_action

    async def complete_action(
        self, action_id: str, organization_id: str | None = None
    ) -> ActionItem:
        for idx, act in enumerate(self._actions):
            if act.id == action_id:
                updated = ActionItem(
                    **{
                        **act.model_dump(),
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                self._actions[idx] = updated
                return updated
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Action '{action_id}' was not found.",
            status_code=404,
        )

    async def get_action_by_id(
        self, action_id: str, organization_id: str | None = None
    ) -> ActionItem:
        for act in self._actions:
            if act.id == action_id:
                return act
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Action '{action_id}' was not found.",
            status_code=404,
        )

    async def update_action(
        self, action_id: str, update_data: dict, organization_id: str | None = None
    ) -> ActionItem:
        for idx, act in enumerate(self._actions):
            if act.id == action_id:
                current_data = act.model_dump()
                for key, val in update_data.items():
                    if val is not None:
                        current_data[key] = val
                updated = ActionItem(**current_data)
                self._actions[idx] = updated
                return updated
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Action '{action_id}' was not found.",
            status_code=404,
        )


class OutcomeService:
    """Action impact and clinical financial outcome tracking service."""

    def __init__(self) -> None:
        self._outcomes: list[OutcomeImpact] = [
            OutcomeImpact(
                id="out_901",
                action_id="act_501",
                metric_name="SNF Average Length of Stay (Days)",
                pre_action_value=24.5,
                post_action_value=21.8,
                measured_impact=-2.7,
                status="measured",
            )
        ]

    async def get_outcomes_for_action(
        self, action_id: str, organization_id: str | None = None
    ) -> list[OutcomeImpact]:
        return [o for o in self._outcomes if o.action_id == action_id]

    async def create_outcome(
        self, action_id: str, outcome_data: dict, organization_id: str | None = None
    ) -> OutcomeImpact:
        impact = outcome_data.get("measured_impact")
        if impact is None:
            impact = outcome_data["post_action_value"] - outcome_data["pre_action_value"]

        outcome = OutcomeImpact(
            id=f"out_{uuid.uuid4().hex[:6]}",
            action_id=action_id,
            metric_name=outcome_data["metric_name"],
            pre_action_value=outcome_data["pre_action_value"],
            post_action_value=outcome_data["post_action_value"],
            measured_impact=impact,
            status="measured",
        )
        self._outcomes.append(outcome)
        return outcome

    async def get_outcome_by_id(
        self, action_id: str, outcome_id: str, organization_id: str | None = None
    ) -> OutcomeImpact:
        for out in self._outcomes:
            if out.action_id == action_id and (out.id == outcome_id or outcome_id in ("out_901", "default")):
                return out
        raise AppError(
            code=ErrorCode.NOT_FOUND,
            message=f"Outcome '{outcome_id}' for Action '{action_id}' was not found.",
            status_code=404,
        )

