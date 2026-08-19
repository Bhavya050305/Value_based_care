"""Generate a valid JWT Bearer token with full ADMIN permissions for Swagger UI authorization."""

from jose import jwt
from app.core.config import get_settings

def generate_token():
    settings = get_settings()
    secret = settings.supabase_jwt_secret or "8AYSVhRZTu5amqHlxuiLDWYVD5muyPWpqAMiFceR0gD1PRDwt5GbwziupDpjKbV9RjHL/MLGjdOttj+nkYbVAA=="
    payload = {
        "sub": "test-user-admin",
        "email": "admin@example.com",
        "role": "admin",
        "organization_id": "org_test",
        "aud": "authenticated",
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    print("\n" + "=" * 70)
    print("FULL ADMIN JWT BEARER TOKEN FOR SWAGGER UI AUTHORIZATION:")
    print("=" * 70)
    print(token)
    print("=" * 70 + "\n")
    return token

if __name__ == "__main__":
    generate_token()
