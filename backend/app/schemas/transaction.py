from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class TransactionBase(BaseModel):
    amount: float
    currency: str = "USD"
    status: str = "pending"
    type: str = "payment"
    payment_method: Optional[str] = None
    provider_transaction_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    booking_id: int

class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    payment_method: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    booking_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PaymentIntentResponse(BaseModel):
    client_secret: str
    transaction_id: int
    amount: float
    currency: str
