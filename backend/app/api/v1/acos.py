"""ACO Explorer & Performance Year API routes."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.aco import AcoDetail, AcoListItem
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.aco import AcoService
from app.services.report_generator import ReportGeneratorService
from app.services.ai_insights import AIInsightsService

router = APIRouter(prefix="", tags=["ACO Explorer"])
service = AcoService()
report_svc = ReportGeneratorService()


@router.get("/performance-years", response_model=ApiResponse[list[int]])
async def get_performance_years(
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[int]]:
    """Dynamically discover available performance years from database."""
    years = await service.get_performance_years(db)
    return ApiResponse(data=years, meta=ResponseMeta(request_id=request_id))


@router.get("/acos", response_model=ApiResponse[list[AcoListItem]])
async def list_acos(
    year: int = Query(..., description="Performance year is required (2022, 2023, 2024)"),
    search: str | None = Query(None, description="Search term for ACO name or identifier"),
    state: str | None = Query(None, description="Filter by state"),
    track: str | None = Query(None, description="Filter by MSSP track"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[AcoListItem]]:
    """List all ACOs belonging strictly to the requested performance year."""
    data = await service.list_acos(db, user.organization_id, search, state, track, year)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/acos/{aco_id}", response_model=ApiResponse[AcoDetail])
async def get_aco_by_id(
    aco_id: str,
    year: int = Query(2024, description="Performance year (2022, 2023, 2024)"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[AcoDetail]:
    """Retrieve detailed ACO information for a specific performance year."""
    data = await service.get_aco_by_id(aco_id, db, user.organization_id, year=year)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/acos/{aco_id}/report")
async def get_aco_report(
    aco_id: str,
    performance_year: int = Query(..., description="Performance year is required"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
):
    """Real-time endpoint to assemble database context and generate executive report narrative."""
    report = await report_svc.generate_report(db, aco_id, performance_year)
    return report


ai_insights_svc = AIInsightsService()


@router.get("/acos/{aco_id}/ai-insights", response_model=ApiResponse[dict])
async def get_aco_ai_insights(
    aco_id: str,
    year: int = Query(..., description="Performance year is required"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
    request_id: str = Depends(get_request_id),
):
    """Generate or retrieve cached ACO-specific AI Insights & Recommendations."""
    data = await ai_insights_svc.get_insights(db, aco_id, year)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/acos/{aco_id}/pdf-report")
async def download_aco_pdf_report(
    aco_id: str,
    year: int = Query(..., description="Performance year is required"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.READ_ACO])),
):
    """Generate and download server-side executive PDF report using ReportLab."""
    pdf_bytes = await report_svc.generate_report_pdf(db, aco_id, year)
    filename = f"ACO_{aco_id}_Performance_Report_{year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
