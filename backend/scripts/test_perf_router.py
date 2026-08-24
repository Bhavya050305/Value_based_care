from fastapi import FastAPI
from fastapi.testclient import TestClient
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api.v1.performance import router as perf_router
from app.core.dependencies import get_current_user
from app.core.security import AuthenticatedUser

app = FastAPI()
app.include_router(perf_router, prefix='/api/v1')

async def _test_user():
    return AuthenticatedUser(
        user_id='test', organization_id=None, role='viewer', permissions=('read:aco',), email='test@example.com'
    )

app.dependency_overrides[get_current_user] = _test_user

client = TestClient(app)
resp = client.get('/api/v1/acos/A3458/financial?year=2021')
print('STATUS', resp.status_code)
print('JSON:', resp.json())
