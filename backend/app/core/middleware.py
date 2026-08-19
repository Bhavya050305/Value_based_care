"""HTTP middleware for request tracing and cross-cutting concerns."""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import get_settings


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to each request and response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        header = settings.request_id_header
        request_id = request.headers.get(header) or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[header] = request_id
        return response
