import pytest
from unittest.mock import MagicMock
from app.services.payment import PaymentService
from app.models.booking import Booking
from app.models.transaction import Transaction

@pytest.fixture
def mock_db():
    return MagicMock()

def test_create_payment_intent(mock_db):
    booking = Booking(id=1, status="pending_payment", total_price=150.0)
    mock_db.query.return_value.filter.return_value.first.return_value = booking
    
    response = PaymentService.create_payment_intent(mock_db, 1)
    
    assert response.amount == 150.0
    assert response.currency == "USD"
    assert "pi_" in response.client_secret

def test_confirm_payment(mock_db):
    transaction = Transaction(id=1, booking_id=10, status="pending")
    booking = Booking(id=10, status="pending_payment")
    
    mock_db.query.return_value.filter.return_value.first.side_effect = [transaction, booking]
    
    updated_tx = PaymentService.confirm_payment(mock_db, 1, "prov_123")
    
    assert updated_tx.status == "completed"
    assert updated_tx.provider_transaction_id == "prov_123"
    assert booking.status == "confirmed"
