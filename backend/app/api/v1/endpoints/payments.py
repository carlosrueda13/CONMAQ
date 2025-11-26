from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.services.payment import PaymentService
from app.schemas.transaction import PaymentIntentResponse, Transaction, TransactionUpdate
from app.models.transaction import Transaction as TransactionModel

router = APIRouter()

@router.post("/create-intent/{booking_id}", response_model=PaymentIntentResponse)
def create_payment_intent(
    booking_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
):
    """
    Create a payment intent for a booking.
    This initiates the payment process.
    """
    # In a real app, verify user owns the booking
    return PaymentService.create_payment_intent(db, booking_id)

@router.post("/confirm/{transaction_id}", response_model=Transaction)
def confirm_payment(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
):
    """
    Confirm a payment (Mock).
    In production, this should be replaced by a Webhook handler or a secure server-side verification.
    """
    # Mock: We accept any provider_id sent by client
    provider_id = payload.provider_transaction_id or "mock_tx_12345"
    return PaymentService.confirm_payment(db, transaction_id, provider_id)

@router.get("/history/{booking_id}", response_model=List[Transaction])
def get_payment_history(
    booking_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_user),
):
    """
    Get all transactions for a specific booking.
    """
    transactions = db.query(TransactionModel).filter(TransactionModel.booking_id == booking_id).all()
    return transactions
