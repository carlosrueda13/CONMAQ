from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.tests.utils.utils import random_email, random_lower_string
from app.tests.utils.user import create_random_user, user_authentication_headers
from app.models.availability import AvailabilitySlot

def test_notification_on_outbid(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    # 1. Setup: Machine and Slot
    # Create machine
    machine_data = {
        "name": "Notification Test Machine",
        "type": "Bulldozer",
        "model": "D6",
        "serial_number": random_lower_string(),
        "location_lat": 0, "location_lng": 0,
        "price_base_per_hour": 100.0,
        "specs": {}
    }
    r = client.post(f"{settings.API_V1_STR}/machines/", headers=superuser_token_headers, json=machine_data)
    machine_id = r.json()["id"]

    # Create slot manually
    start_time = datetime.now(timezone.utc) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    slot = AvailabilitySlot(
        machine_id=machine_id,
        start_time=start_time,
        end_time=end_time,
        is_available=True,
        base_price=100.0,
        auction_end_time=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    slot_id = slot.id

    # 2. User A places a bid
    user_a_email = random_email()
    user_a_pass = random_lower_string()
    user_a = create_random_user(db, email=user_a_email, password=user_a_pass)
    headers_a = user_authentication_headers(client, user_a_email, user_a_pass)

    bid_data_a = {"slot_id": slot_id, "max_bid": 150.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_a, json=bid_data_a)
    assert r.status_code == 200

    # 3. User B outbids User A
    user_b_email = random_email()
    user_b_pass = random_lower_string()
    user_b = create_random_user(db, email=user_b_email, password=user_b_pass)
    headers_b = user_authentication_headers(client, user_b_email, user_b_pass)

    bid_data_b = {"slot_id": slot_id, "max_bid": 200.0}
    r = client.post(f"{settings.API_V1_STR}/offers/", headers=headers_b, json=bid_data_b)
    assert r.status_code == 200

    # 4. Check User A's notifications
    r = client.get(f"{settings.API_V1_STR}/notifications/", headers=headers_a)
    assert r.status_code == 200
    notifications = r.json()
    assert len(notifications) > 0
    
    # Find the outbid notification
    outbid_notif = next((n for n in notifications if n["type"] == "outbid"), None)
    assert outbid_notif is not None
    assert outbid_notif["is_read"] is False
    assert "superada" in outbid_notif["message"]

    # 5. Mark as read
    notif_id = outbid_notif["id"]
    r = client.put(f"{settings.API_V1_STR}/notifications/{notif_id}/read", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["is_read"] is True

    # Verify it is read
    r = client.get(f"{settings.API_V1_STR}/notifications/", headers=headers_a)
    notifications = r.json()
    outbid_notif = next((n for n in notifications if n["id"] == notif_id), None)
    assert outbid_notif["is_read"] is True
