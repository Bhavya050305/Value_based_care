"""FastAPI dependency injection wiring."""

import uuid
from collections.abc import Callable

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, ErrorCode
from app.core.security import (
    AuthenticatedUser,
    Permission,
    UserRole,
    decode_jwt_token,
    get_user_from_token_payload,
)

security_bearer = HTTPBearer(auto_error=False)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or str(uuid.uuid4())


def get_app_settings() -> Settings:
    return get_settings()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> AuthenticatedUser:
    """Extract and validate current authenticated user from Bearer token."""
    if not credentials or not credentials.credentials:
        raise AppError(
            code=ErrorCode.AUTHENTICATION,
            message="Authentication credentials (Bearer token) were not provided.",
            status_code=401,
        )

    token = credentials.credentials
    payload = decode_jwt_token(token)
    return get_user_from_token_payload(payload)


def require_role(allowed_roles: list[UserRole | str]) -> Callable:
    """Dependency factory requiring user to possess one of the allowed roles."""
    allowed = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]

    async def role_checker(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role == UserRole.ADMIN.value or Permission.ADMIN_ALL.value in user.permissions:
            return user
        if user.role not in allowed:
            raise AppError(
                code=ErrorCode.AUTHORIZATION,
                message=f"Role '{user.role}' is not authorized for this resource.",
                status_code=403,
            )
        return user

    return role_checker


def require_permissions(required_permissions: list[Permission | str]) -> Callable:
    """Dependency factory requiring user to possess specified permissions."""
    required = [
        p.value if isinstance(p, Permission) else str(p) for p in required_permissions
    ]

    async def permission_checker(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role == UserRole.ADMIN.value or Permission.ADMIN_ALL.value in user.permissions:
            return user
        user_perms = set(user.permissions)
        missing = [p for p in required if p not in user_perms]
        if missing:
            raise AppError(
                code=ErrorCode.AUTHORIZATION,
                message=f"Missing required permission(s): {', '.join(missing)}.",
                status_code=403,
            )
        return user

    return permission_checker

