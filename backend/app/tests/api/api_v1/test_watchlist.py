from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.utils import random_email, random_lower_string
from app.tests.utils.user import create_random_user, user_authentication_headers

def test_toggle_watchlist(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # Create a machine first (need admin)
    data = {
        "name": "Excavator Watchlist Test",
        "type": "Excavator",
        "model": "CAT 320",
        "serial_number": random_lower_string(),
        "location_lat": 10.0,
        "location_lng": -74.0,
        "price_base_per_hour": 100.0,
        "specs": {"power": "200hp"}
    }
    r = client.post(
        f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=data
    )
    assert r.status_code == 200
    machine_id = r.json()["id"]

    # Create a normal user
    user_email = random_email()
    user_password = random_lower_string()
    user = create_random_user(db, email=user_email, password=user_password)
    headers = user_authentication_headers(client, user_email, user_password)

    # Add to watchlist
    r = client.post(
        f"{settings.API_V1_STR}/watchlist/toggle",
        headers=headers,
        json={"machine_id": machine_id}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "added"

    # Verify it's in the list
    r = client.get(f"{settings.API_V1_STR}/watchlist/", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["machine_id"] == machine_id

    # Remove from watchlist
    r = client.post(
        f"{settings.API_V1_STR}/watchlist/toggle",
        headers=headers,
        json={"machine_id": machine_id}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "removed"

    # Verify it's gone
    r = client.get(f"{settings.API_V1_STR}/watchlist/", headers=headers)
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0
