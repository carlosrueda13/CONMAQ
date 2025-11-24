from fastapi.testclient import TestClient
from app.core.config import settings
import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def test_create_machine(client: TestClient, superuser_token_headers: dict) -> None:
    data = {
        "name": "Test Excavator",
        "serial_number": f"SN{random_string()}",
        "description": "A test machine",
        "specs": {"weight": "20t"},
        "capacity_m3h": 100,
        "fuel_type": "diesel",
        "tank_capacity": 200,
        "price_base_per_hour": 150.0,
        "min_hours": 4,
        "location_lat": 4.0,
        "location_lng": -74.0,
        "address": "Test Address",
        "photos": [],
        "status": "available"
    }
    response = client.post(
        f"{settings.API_V1_STR}/machines/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content

def test_read_machine(client: TestClient, superuser_token_headers: dict) -> None:
    # Create a machine first
    data = {
        "name": "Read Test Machine",
        "serial_number": f"SN{random_string()}",
        "price_base_per_hour": 100.0,
        "status": "available"
    }
    create_res = client.post(
        f"{settings.API_V1_STR}/machines/",
        headers=superuser_token_headers,
        json=data,
    )
    machine_id = create_res.json()["id"]

    # Read it
    response = client.get(f"{settings.API_V1_STR}/machines/{machine_id}")
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["id"] == machine_id
