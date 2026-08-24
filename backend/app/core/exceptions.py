"""Centralized application exceptions and error codes."""

from enum import Enum


class StrEnum(str, Enum):
    """Backport-friendly string enum (stdlib StrEnum requires Python 3.11+)."""


class ErrorCode(StrEnum):
    VALIDATION = "VALIDATION_ERROR"
    AUTHENTICATION = "AUTHENTICATION_ERROR"
    AUTHORIZATION = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    DATABASE = "DATABASE_ERROR"
    ML = "ML_ERROR"
    SIMULATION = "SIMULATION_ERROR"
    AI = "AI_ERROR"
    RAG = "RAG_ERROR"
    REPORT = "REPORT_ERROR"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"


class AppError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        status_code: int = 400,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
