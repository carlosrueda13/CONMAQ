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

def test_booking_lifecycle(client: TestClient, superuser_token_headers: dict):
    # 1. Setup: Create Machine & Slot
    machine_data = {
        "name": f"Machine Booking {random_string()}",
        "serial_number": f"SN{random_string()}",
        "price_base_per_hour": 100.0,
        "status": "available"
    }
    r = client.post(f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=machine_data)
    assert r.status_code == 200
    machine_id = r.json()["id"]

    client.post(f"{settings.API_V1_STR}/machines/{machine_id}/availability/generate", headers=superuser_token_headers, params={"days": 1})
    slots = client.get(f"{settings.API_V1_STR}/machines/{machine_id}/availability").json()
    slot_id = slots[0]["id"]

    # 2. User A places a winning bid
    headers_a = create_user(client)
    bid_data = {"slot_id": slot_id, "amount": 150.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_a, json=bid_data)
    assert r.status_code == 200
    offer_data = r.json()
    offer_id = offer_data["offer_id"]

    # 3. Create Booking from Offer
    r = client.post(f"{settings.API_V1_STR}/bookings/from-offer/{offer_id}", headers=headers_a)
    assert r.status_code == 200
    booking_data = r.json()
    booking_id = booking_data["id"]
    assert booking_data["status"] == "pending_payment"
    assert booking_data["total_price"] == 150.0

    # 4. Payment Flow
    # Create Payment Intent
    r = client.post(f"{settings.API_V1_STR}/payments/create-intent/{booking_id}", headers=headers_a)
    assert r.status_code == 200
    payment_data = r.json()
    transaction_id = payment_data["transaction_id"]
    assert "client_secret" in payment_data

    # Confirm Payment
    confirm_data = {"provider_transaction_id": "test_stripe_123", "status": "completed"}
    r = client.post(f"{settings.API_V1_STR}/payments/confirm/{transaction_id}", headers=headers_a, json=confirm_data)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"

    # Verify Booking is now confirmed
    # We need to fetch the booking again or check the response of confirm_payment if it returns booking?
    # The confirm_payment endpoint returns the Transaction, but updates the Booking.
    # Let's fetch the booking.
    # Wait, there is no GET /bookings/{id} endpoint for users in the provided context (only list).
    # But we can list and filter or use superuser to list all.
    # Let's use the list endpoint for the user.
    r = client.get(f"{settings.API_V1_STR}/bookings/", headers=headers_a)
    bookings = r.json()
    my_booking = next(b for b in bookings if b["id"] == booking_id)
    assert my_booking["status"] == "confirmed"

    # 5. Operations: Check-in
    check_in_data = {
        "start_fuel_level": 100.0,
        "start_photos": ["http://photo1.jpg"]
    }
    r = client.post(f"{settings.API_V1_STR}/bookings/{booking_id}/check-in", headers=headers_a, json=check_in_data)
    assert r.status_code == 200
    assert r.json()["status"] == "active"

    # 6. Operations: Check-out
    check_out_data = {
        "end_fuel_level": 90.0,
        "end_photos": ["http://photo2.jpg"]
    }
    r = client.post(f"{settings.API_V1_STR}/bookings/{booking_id}/check-out", headers=headers_a, json=check_out_data)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
