from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Shared properties
class OfferBase(BaseModel):
    max_bid: Optional[float] = None

# Properties to receive on creation
class OfferCreate(OfferBase):
    slot_id: int
    amount: float # The immediate bid amount
    max_bid: Optional[float] = None # Optional: If provided, enables proxy bidding up to this value

# Properties to return to client
class Offer(OfferBase):
    id: int
    amount: float
    user_id: int
    slot_id: int
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class OfferInDB(Offer):
    pass
