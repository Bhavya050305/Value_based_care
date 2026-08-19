"""Authentication and user profile response schemas."""

from pydantic import BaseModel


class UserProfileData(BaseModel):
    user_id: str
    organization_id: str | None = None
    role: str | None = None
    permissions: list[str] = []
    email: str | None = None
    mfa_verified: bool | None = None
