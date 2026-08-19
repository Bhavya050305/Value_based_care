"""Health and readiness response schemas."""

from pydantic import BaseModel

from app.schemas.common import DataAvailability


class HealthData(BaseModel):
    status: str
    version: str
    environment: str


class ReadinessChecks(BaseModel):
    database: DataAvailability
    redis: DataAvailability


class ReadinessData(BaseModel):
    status: str
    checks: ReadinessChecks
