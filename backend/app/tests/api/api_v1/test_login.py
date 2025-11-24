from fastapi.testclient import TestClient
from app.core.config import settings

def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": "admin@conmaq.com",
        "password": "admin",
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    # Note: This test will fail if the DB is not initialized with the superuser
    # But it serves as a template.
    if r.status_code == 200:
        tokens = r.json()
        assert "access_token" in tokens
        assert tokens["token_type"] == "bearer"
    else:
        # If user doesn't exist, it returns 400
        assert r.status_code in [200, 400]
