"""Common API response envelopes and data availability contracts."""

from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar


class StrEnum(str, Enum):
    """Backport-friendly string enum (stdlib StrEnum requires Python 3.11+)."""

from pydantic import BaseModel, Field

T = TypeVar("T")


class DataStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    NO_DATA_AVAILABLE = "NO_DATA_AVAILABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    INSUFFICIENT_FEATURES = "INSUFFICIENT_FEATURES"


class PaginationMeta(BaseModel):
    page: int = 1
    page_size: int = 20
    total_items: int = 0
    total_pages: int = 0


class ResponseMeta(BaseModel):
    request_id: str | None = None
    pagination: PaginationMeta | None = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: ResponseMeta | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class DataAvailability(BaseModel):
    """Explicit unavailable-state contract used across analytics, ML, and AI."""

    available: bool
    value: Any | None = None
    data_status: DataStatus | None = None
    reason: str | None = None
    source: str | None = None
    required_source: str | None = None
    last_updated: datetime | None = None
