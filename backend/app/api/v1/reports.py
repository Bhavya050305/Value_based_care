"""Reports API routes."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_request_id, require_permissions
from app.core.security import AuthenticatedUser, Permission
from app.schemas.assistant import ReportCreateRequest, ReportItem
from app.schemas.common import ApiResponse, ResponseMeta
from app.services.assistant import ReportService
from app.services.report_generator import ReportGeneratorService

router = APIRouter(prefix="/reports", tags=["Reports"])
service = ReportService()
report_gen_svc = ReportGeneratorService()


@router.get("", response_model=ApiResponse[list[ReportItem]])
async def list_reports(
    user: AuthenticatedUser = Depends(require_permissions([Permission.GENERATE_REPORTS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[list[ReportItem]]:
    data = await service.list_reports(user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.post("", response_model=ApiResponse[ReportItem])
async def create_report(
    request_body: ReportCreateRequest,
    user: AuthenticatedUser = Depends(require_permissions([Permission.GENERATE_REPORTS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ReportItem]:
    data = await service.create_report(request_body, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/{report_id}", response_model=ApiResponse[ReportItem])
async def get_report_by_id(
    report_id: str,
    user: AuthenticatedUser = Depends(require_permissions([Permission.GENERATE_REPORTS])),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ReportItem]:
    """Return report status and details."""
    data = await service.get_report_by_id(report_id, user.organization_id)
    return ApiResponse(data=data, meta=ResponseMeta(request_id=request_id))


@router.get("/aco/{aco_id}")
async def generate_realtime_aco_report(
    aco_id: str,
    performance_year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.GENERATE_REPORTS])),
):
    """Generate real-time executive report for specified ACO and performance year."""
    report = await report_gen_svc.generate_report(db, aco_id, performance_year)
    return report


@router.get("/aco/{aco_id}/pdf")
async def generate_realtime_aco_pdf_report(
    aco_id: str,
    year: int = Query(2024, description="Performance year"),
    db: AsyncSession = Depends(get_db_session),
    user: AuthenticatedUser = Depends(require_permissions([Permission.GENERATE_REPORTS])),
):
    """Generate server-side executive PDF report for specified ACO and performance year."""
    pdf_bytes = await report_gen_svc.generate_report_pdf(db, aco_id, year)
    filename = f"ACO_{aco_id}_Performance_Report_{year}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
