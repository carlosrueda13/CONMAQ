from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.booking import Booking
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, PaymentIntentResponse
import uuid

class PaymentService:
    
    @staticmethod
    def create_payment_intent(db: Session, booking_id: int) -> PaymentIntentResponse:
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.status != "pending_payment":
            raise HTTPException(status_code=400, detail="Booking is not pending payment")

        # Create a pending transaction record
        transaction = Transaction(
            booking_id=booking.id,
            amount=booking.total_price,
            currency="USD",
            status="pending",
            type="payment"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # MOCK: Generate a fake client_secret (In real Stripe, this comes from stripe.PaymentIntent.create)
        # Format: pi_<random>_secret_<random>
        mock_client_secret = f"pi_{uuid.uuid4().hex[:10]}_secret_{uuid.uuid4().hex[:10]}"
        
        return PaymentIntentResponse(
            client_secret=mock_client_secret,
            transaction_id=transaction.id,
            amount=transaction.amount,
            currency=transaction.currency
        )

    @staticmethod
    def confirm_payment(db: Session, transaction_id: int, provider_id: str):
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.status == "completed":
            return transaction # Already processed

        # Update Transaction
        transaction.status = "completed"
        transaction.provider_transaction_id = provider_id
        transaction.payment_method = "card" # Mock assumption
        
        # Update Booking Status
        booking = db.query(Booking).filter(Booking.id == transaction.booking_id).first()
        if booking:
            booking.status = "confirmed"
            db.add(booking)
            
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def fail_payment(db: Session, transaction_id: int, reason: str):
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
            
        transaction.status = "failed"
        # We could log the reason in a new field or logs
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def get_payment_history(db: Session, booking_id: int) -> List[Transaction]:
        return db.query(Transaction).filter(Transaction.booking_id == booking_id).all()
