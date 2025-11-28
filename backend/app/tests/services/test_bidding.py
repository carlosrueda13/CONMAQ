import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from app.services.bidding import place_bid, MIN_INCREMENT, SOFT_CLOSE_MINUTES, SOFT_CLOSE_EXTENSION
from app.models.availability import AvailabilitySlot
from app.models.offer import Offer
from app.models.user import User

# Mock DB Session
@pytest.fixture
def mock_db():
    return MagicMock()

# Mock Slot
@pytest.fixture
def mock_slot():
    slot = AvailabilitySlot()
    slot.id = 1
    slot.is_available = True
    slot.base_price = 100.0
    slot.current_price = None
    slot.winner_id = None
    slot.auction_end_time = datetime.now(timezone.utc) + timedelta(hours=1)
    return slot

def test_place_bid_first_bid(mock_db, mock_slot):
    """Test placing the first bid on a slot."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot
    
    user_id = 101
    amount = 120.0
    
    slot, offer = place_bid(mock_db, 1, user_id, amount)
    
    assert slot.winner_id == user_id
    # Logic says if no current price, it takes base price or amount. 
    # In code: if slot.current_price is None: slot.current_price = amount (if base was None)
    # But mock_slot has base_price=100.0.
    # Code: slot.current_price = slot.base_price (100.0)
    assert slot.current_price == 100.0 
    assert offer.status == "winning"
    assert offer.max_bid == 120.0

def test_place_bid_manual_outbid(mock_db, mock_slot):
    """Test a manual bid outbidding an existing manual bid."""
    # Setup existing winner
    mock_slot.current_price = 120.0
    mock_slot.winner_id = 101
    
    # Existing winning offer
    existing_offer = Offer(user_id=101, slot_id=1, amount=120.0, max_bid=120.0, status="winning")
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_slot, existing_offer]
    
    new_user_id = 102
    new_amount = 140.0 # > 120 + 10
    
    slot, new_offer = place_bid(mock_db, 1, new_user_id, new_amount)
    
    # New price should be old max (120) + increment (10) = 130
    assert slot.winner_id == new_user_id
    assert slot.current_price == 130.0
    assert new_offer.status == "winning"
    assert existing_offer.status == "outbid"

def test_place_bid_proxy_defense(mock_db, mock_slot):
    """Test that a high max_bid defends against a lower new bid."""
    # Setup existing winner with high proxy
    mock_slot.current_price = 120.0
    mock_slot.winner_id = 101
    
    # Existing winning offer has max_bid = 200
    existing_offer = Offer(user_id=101, slot_id=1, amount=120.0, max_bid=200.0, status="winning")
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_slot, existing_offer]
    
    new_user_id = 102
    new_amount = 150.0 # Valid bid (> 120 + 10) but < 200
    
    slot, new_offer = place_bid(mock_db, 1, new_user_id, new_amount)
    
    # Winner should still be 101
    assert slot.winner_id == 101
    # Price should rise to new_amount (150) + increment (10) = 160
    assert slot.current_price == 160.0
    assert new_offer.status == "outbid"

def test_place_bid_proxy_overtake(mock_db, mock_slot):
    """Test that a new proxy bid overtakes an existing proxy bid."""
    # Setup existing winner
    mock_slot.current_price = 160.0
    mock_slot.winner_id = 101
    
    # Existing max is 200
    existing_offer = Offer(user_id=101, slot_id=1, amount=120.0, max_bid=200.0, status="winning")
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_slot, existing_offer]
    
    new_user_id = 102
    new_amount = 250.0 # > 200
    
    slot, new_offer = place_bid(mock_db, 1, new_user_id, new_amount)
    
    # Winner changes to 102
    assert slot.winner_id == 102
    # Price becomes old max (200) + increment (10) = 210
    assert slot.current_price == 210.0
    assert new_offer.status == "winning"
    assert existing_offer.status == "outbid"

def test_soft_close_extension(mock_db, mock_slot):
    """Test that bidding near the end extends the auction time."""
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot
    
    # Set end time to 2 minutes from now (within SOFT_CLOSE_MINUTES = 5)
    now = datetime.now(timezone.utc)
    mock_slot.auction_end_time = now + timedelta(minutes=2)
    original_end_time = mock_slot.auction_end_time
    
    place_bid(mock_db, 1, 101, 120.0)
    
    # Should be extended
    expected_extension = timedelta(minutes=SOFT_CLOSE_EXTENSION)
    assert mock_slot.auction_end_time > original_end_time
    # Allow small delta for execution time
    assert (mock_slot.auction_end_time - original_end_time).total_seconds() == expected_extension.total_seconds()

def test_bid_too_low(mock_db, mock_slot):
    """Test that a bid lower than minimum increment is rejected."""
    mock_slot.current_price = 100.0
    mock_db.query.return_value.filter.return_value.first.return_value = mock_slot
    
    # Min required is 100 + 10 = 110
    with pytest.raises(HTTPException) as excinfo:
        place_bid(mock_db, 1, 101, 105.0)
    
    assert excinfo.value.status_code == 400
    assert "Bid too low" in excinfo.value.detail
