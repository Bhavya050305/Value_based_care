from fastapi.testclient import TestClient
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import create_app
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user

app = create_app()

# Override get_current_user to bypass auth for the test
async def _test_user():
    return AuthenticatedUser(
        user_id='test-user',
        organization_id=None,
        role='viewer',
        permissions=('read:aco',),
        email='test@example.com',
        mfa_verified=False,
    )

app.dependency_overrides[get_current_user] = _test_user

client = TestClient(app)

resp = client.get('/api/v1/acos/A3458/financial?year=2021')
print('STATUS', resp.status_code)
print('JSON:', resp.json())
