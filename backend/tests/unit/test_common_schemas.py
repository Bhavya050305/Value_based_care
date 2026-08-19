"""Unit tests for shared API schemas."""

from app.schemas.common import DataAvailability, DataStatus, ErrorResponse


def test_data_availability_unavailable_state():
    payload = DataAvailability(
        available=False,
        value=None,
        data_status=DataStatus.INSUFFICIENT_DATA,
        reason="Required source data is not available.",
    )
    assert payload.available is False
    assert payload.data_status == DataStatus.INSUFFICIENT_DATA


def test_error_response_envelope():
    response = ErrorResponse(
        error={
            "code": "NOT_FOUND",
            "message": "Resource not found",
            "request_id": "test-request-id",
        }
    )
    assert response.success is False
    assert response.error.code == "NOT_FOUND"
