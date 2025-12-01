import pytest
from unittest.mock import MagicMock
from datetime import datetime
from app.services.booking import create_booking_from_offer, perform_check_in
from app.models.offer import Offer
from app.models.availability import AvailabilitySlot
from app.models.booking import Booking
from app.schemas.booking import BookingCheckIn

@pytest.fixture
def mock_db():
    return MagicMock()

def test_create_booking_from_offer(mock_db):
    # Setup
    offer = Offer(id=1, user_id=101, slot_id=5, amount=200.0)
    slot = AvailabilitySlot(id=5, machine_id=10, start_time=datetime.now(), end_time=datetime.now())
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [offer, slot]
    
    booking = create_booking_from_offer(mock_db, 1)
    
    assert booking.user_id == 101
    assert booking.machine_id == 10
    assert booking.total_price == 200.0
    assert booking.status == "pending_payment"

def test_perform_check_in(mock_db):
    booking = Booking(id=1, status="confirmed")
    mock_db.query.return_value.filter.return_value.first.return_value = booking
    
    check_in_data = BookingCheckIn(start_fuel_level=0.8, start_photos=["url1"])
    
    updated_booking = perform_check_in(mock_db, 1, check_in_data)
    
    assert updated_booking.status == "active"
    assert updated_booking.start_fuel_level == 0.8
