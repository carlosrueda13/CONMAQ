from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Transaction(Base):
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("booking.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(String, default="pending") # pending, completed, failed, refunded
    
    provider_transaction_id = Column(String, nullable=True) # e.g., Stripe PaymentIntent ID
    payment_method = Column(String, nullable=True) # card, bank_transfer
    type = Column(String, default="payment") # payment, refund, deposit
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    booking = relationship("Booking", backref="transactions")
