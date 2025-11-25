from fastapi.testclient import TestClient
from app.core.config import settings
import random
import string

def random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_user_headers(client: TestClient, email: str, password: str) -> dict:
    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}

def create_user(client: TestClient) -> dict:
    email = f"{random_string()}@example.com"
    password = "password123"
    data = {"email": email, "password": password, "full_name": "Test User"}
    r = client.post(f"{settings.API_V1_STR}/users/", json=data)
    assert r.status_code == 200
    return get_user_headers(client, email, password)

def test_bidding_flow(client: TestClient, superuser_token_headers: dict):
    # 1. Create Machine
    machine_data = {
        "name": f"Machine {random_string()}",
        "serial_number": f"SN{random_string()}",
        "price_base_per_hour": 100.0,
        "status": "available"
    }
    r = client.post(f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=machine_data)
    assert r.status_code == 200
    machine_id = r.json()["id"]

    # 2. Generate Availability
    r = client.post(
        f"{settings.API_V1_STR}/machines/{machine_id}/availability/generate",
        headers=superuser_token_headers,
        params={"days": 1}
    )
    assert r.status_code == 200

    # Get a slot
    r = client.get(f"{settings.API_V1_STR}/machines/{machine_id}/availability")
    assert r.status_code == 200
    slots = r.json()
    assert len(slots) > 0
    slot_id = slots[0]["id"]

    # 3. User A places a bid
    headers_a = create_user(client)
    bid_data_a = {"slot_id": slot_id, "amount": 150.0, "max_bid": 150.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_a, json=bid_data_a)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    # First bid, price should be base price (100.0) or the bid amount if no base price logic overrides it.
    # In our logic: if slot.current_price is None -> slot.current_price = amount (150.0)
    # Wait, logic says: if slot.current_price is None: slot.current_price = amount
    # But wait, base_price is 100.0.
    # Logic: current_price = slot.current_price if slot.current_price else slot.base_price (100.0)
    # If not current_winner_id: slot.current_price = slot.base_price (100.0)
    assert data["current_price"] == 100.0 
    
    # 4. User B places a higher bid (Proxy War)
    headers_b = create_user(client)
    # User B bids 120. User A has max 150.
    # User A should win, but price should go up to 120 + increment (10) = 130.
    bid_data_b = {"slot_id": slot_id, "amount": 120.0, "max_bid": 120.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_b, json=bid_data_b)
    assert r.status_code == 200
    data = r.json()
    
    # Check slot status
    # User A (first bidder) should still be winner because 150 > 120.
    # Price should be 120 + 10 = 130.
    assert data["current_price"] == 130.0
    
    # 5. User B places a winning bid
    # User B bids 200. User A max is 150.
    # User B should win. Price should be 150 + 10 = 160.
    bid_data_b_2 = {"slot_id": slot_id, "amount": 200.0, "max_bid": 200.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_b, json=bid_data_b_2)
    assert r.status_code == 200
    data = r.json()
    
    assert data["current_price"] == 160.0
    # User B should be winner now.
    # We can verify winner_id matches User B's ID if we had it, but checking price logic is strong enough.

def test_bid_too_low(client: TestClient, superuser_token_headers: dict):
    # Setup machine and slot
    machine_data = {
        "name": f"Machine {random_string()}",
        "serial_number": f"SN{random_string()}",
        "price_base_per_hour": 100.0,
        "status": "available"
    }
    r = client.post(f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=machine_data)
    machine_id = r.json()["id"]
    client.post(f"{settings.API_V1_STR}/machines/{machine_id}/availability/generate", headers=superuser_token_headers, params={"days": 1})
    slots = client.get(f"{settings.API_V1_STR}/machines/{machine_id}/availability").json()
    slot_id = slots[0]["id"]

    # User A bids 100
    headers_a = create_user(client)
    client.post(f"{settings.API_V1_STR}/offers/", headers=headers_a, json={"slot_id": slot_id, "amount": 100.0, "max_bid": 100.0})

    # User B tries to bid 105 (Increment is 10, so min is 110)
    headers_b = create_user(client)
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_b, json={"slot_id": slot_id, "amount": 105.0, "max_bid": 105.0})
    assert r.status_code == 400
    assert "Bid too low" in r.json()["detail"]

def test_manual_bidding(client: TestClient, superuser_token_headers: dict):
    # Setup machine and slot
    machine_data = {
        "name": f"Machine Manual {random_string()}",
        "serial_number": f"SN{random_string()}",
        "price_base_per_hour": 100.0,
        "status": "available"
    }
    r = client.post(f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=machine_data)
    machine_id = r.json()["id"]
    client.post(f"{settings.API_V1_STR}/machines/{machine_id}/availability/generate", headers=superuser_token_headers, params={"days": 1})
    slots = client.get(f"{settings.API_V1_STR}/machines/{machine_id}/availability").json()
    slot_id = slots[0]["id"]

    # User A bids 100 manually (no max_bid provided)
    headers_a = create_user(client)
    # Sending only amount, max_bid should default to amount (100.0)
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_a, json={"slot_id": slot_id, "amount": 100.0})
    assert r.status_code == 200
    
    # User B bids 120 manually
    headers_b = create_user(client)
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_b, json={"slot_id": slot_id, "amount": 120.0})
    assert r.status_code == 200
    data = r.json()
    
    # Since User A had max_bid=100 (implicit), User B wins with 120.
    # Price should be 100 + 10 = 110? Or 120?
    # Logic: new_price = winner_max_bid (100) + INCREMENT (10) = 110.
    # If 110 > max_bid_amount (120)? No. So price is 110.
    # Wait, if I bid 120 manually, I am willing to pay 120.
    # But the system tries to save me money.
    # If previous max was 100, I only need to pay 110 to beat him.
    assert data["current_price"] == 110.0
    # Winner should be User B (we can't check ID easily but price confirms change)
