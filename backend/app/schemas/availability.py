from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AvailabilitySlotBase(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    base_price: Optional[float] = None

class AvailabilitySlotCreate(AvailabilitySlotBase):
    machine_id: int

class AvailabilitySlotUpdate(BaseModel):
    is_available: Optional[bool] = None
    base_price: Optional[float] = None

class AvailabilitySlot(AvailabilitySlotBase):
    id: int
    machine_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
