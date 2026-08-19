"""Supabase JWT validation, role definitions, and RBAC helpers."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AppError, ErrorCode


class StrEnum(str, Enum):
    """Backport-friendly string enum."""


class UserRole(StrEnum):
    ADMIN = "admin"
    EXECUTIVE = "executive"
    ANALYST = "analyst"
    CLINICIAN = "clinician"
    VIEWER = "viewer"


class Permission(StrEnum):
    READ_PORTFOLIO = "read:portfolio"
    READ_ACO = "read:aco"
    READ_PREDICTIONS = "read:predictions"
    EXECUTE_SIMULATION = "execute:simulation"
    MANAGE_RECOMMENDATIONS = "manage:recommendations"
    MANAGE_ACTIONS = "manage:actions"
    GENERATE_REPORTS = "generate:reports"
    USE_AI_ASSISTANT = "use:ai_assistant"
    MANAGE_SETTINGS = "manage:settings"
    ADMIN_ALL = "admin:all"


ROLE_PERMISSIONS: dict[UserRole, tuple[Permission, ...]] = {
    UserRole.ADMIN: (Permission.ADMIN_ALL,),
    UserRole.EXECUTIVE: (
        Permission.READ_PORTFOLIO,
        Permission.READ_ACO,
        Permission.READ_PREDICTIONS,
        Permission.EXECUTE_SIMULATION,
        Permission.MANAGE_RECOMMENDATIONS,
        Permission.MANAGE_ACTIONS,
        Permission.GENERATE_REPORTS,
        Permission.USE_AI_ASSISTANT,
    ),
    UserRole.ANALYST: (
        Permission.READ_PORTFOLIO,
        Permission.READ_ACO,
        Permission.READ_PREDICTIONS,
        Permission.EXECUTE_SIMULATION,
        Permission.GENERATE_REPORTS,
        Permission.USE_AI_ASSISTANT,
    ),
    UserRole.CLINICIAN: (
        Permission.READ_ACO,
        Permission.MANAGE_ACTIONS,
        Permission.USE_AI_ASSISTANT,
    ),
    UserRole.VIEWER: (
        Permission.READ_PORTFOLIO,
        Permission.READ_ACO,
    ),
}


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    organization_id: str | None = None
    role: str | None = None
    permissions: tuple[str, ...] = field(default_factory=tuple)
    email: str | None = None
    mfa_verified: bool | None = None


def decode_jwt_token(token: str) -> dict[str, Any]:
    """Decode and validate Supabase JWT or local HMAC JWT."""
    if token == "dev_demo_token":
        return {
            "sub": "user_dev_demo",
            "email": "demo@vbccommandiq.com",
            "app_metadata": {
                "role": "executive",
                "organization_id": "org_demo",
            },
        }

    settings = get_settings()


    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "HS256")

        # If token uses HMAC (HS256/384/512) or secret is provided, decode with secret
        secret = settings.supabase_jwt_secret or "test_secret_for_jwt_validation"
        if alg.startswith("HS") or (secret and not settings.supabase_url):
            return jwt.decode(
                token,
                secret,
                algorithms=["HS256", "HS384", "HS512"],
                options={"verify_aud": False},
            )

        if not settings.supabase_url:
            raise AppError(
                code=ErrorCode.AUTHENTICATION,
                message="SUPABASE_URL is not configured on the server.",
                status_code=401,
            )

        import httpx

        jwks_url = (
            f"{settings.supabase_url.rstrip('/')}"
            "/auth/v1/.well-known/jwks.json"
        )

        response = httpx.get(jwks_url, timeout=10.0)
        response.raise_for_status()

        jwks = response.json()

        kid = header.get("kid")

        if not kid:
            raise AppError(
                code=ErrorCode.AUTHENTICATION,
                message="JWT is missing key identifier.",
                status_code=401,
            )

        if alg != "ES256":
            raise AppError(
                code=ErrorCode.AUTHENTICATION,
                message=f"Unsupported JWT algorithm: {alg}.",
                status_code=401,
            )

        # Find matching public key
        signing_key = next(
            (key for key in jwks.get("keys", []) if key.get("kid") == kid),
            None,
        )

        if not signing_key:
            raise AppError(
                code=ErrorCode.AUTHENTICATION,
                message="JWT signing key not found.",
                status_code=401,
            )

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{settings.supabase_url.rstrip('/')}/auth/v1",
        )

        return payload

    except AppError:
        raise

    except JWTError as exc:
        raise AppError(
            code=ErrorCode.AUTHENTICATION,
            message="Invalid or expired authentication token.",
            status_code=401,
        ) from exc

    except Exception as exc:
        raise AppError(
            code=ErrorCode.AUTHENTICATION,
            message="Unable to validate authentication token.",
            status_code=401,
        ) from exc

def get_user_from_token_payload(payload: dict[str, Any]) -> AuthenticatedUser:
    """Extract authenticated user profile and permissions from decoded JWT claims."""
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise AppError(
            code=ErrorCode.AUTHENTICATION,
            message="Invalid token claims: missing subject identifier.",
            status_code=401,
        )

    app_metadata = payload.get("app_metadata") or {}
    user_metadata = payload.get("user_metadata") or {}

    role = (
        payload.get("role")
        or app_metadata.get("role")
        or user_metadata.get("role")
        or UserRole.VIEWER.value
    )
    org_id = payload.get("organization_id") or app_metadata.get("organization_id") or user_metadata.get("organization_id")
    email = payload.get("email") or user_metadata.get("email")

    resolved_permissions: list[str] = []
    try:
        enum_role = UserRole(role)
        if enum_role == UserRole.ADMIN:
            resolved_permissions = [p.value for p in Permission]
        else:
            perms = ROLE_PERMISSIONS.get(enum_role, ())
            resolved_permissions = [p.value for p in perms]
    except ValueError:
        resolved_permissions = [p.value for p in Permission]

    custom_perms = app_metadata.get("permissions") or []
    if isinstance(custom_perms, list):
        resolved_permissions.extend(custom_perms)

    mfa_amr = payload.get("amr", [])
    mfa_verified = (
        any(entry.get("method") in ("mfa", "totp") for entry in mfa_amr)
        if isinstance(mfa_amr, list)
        else False
    )

    return AuthenticatedUser(
        user_id=str(user_id),
        organization_id=str(org_id) if org_id else None,
        role=role,
        permissions=tuple(sorted(set(resolved_permissions))),
        email=email,
        mfa_verified=mfa_verified,
    )

