from typing import Generator, Dict
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> Dict[str, str]:
    login_data = {
        "username": "admin@conmaq.com",
        "password": "admin",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
