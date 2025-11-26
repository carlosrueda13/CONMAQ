from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Shared properties
class BookingBase(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = "pending_payment"
    total_price: Optional[float] = None

# Properties to receive on creation
class BookingCreate(BookingBase):
    user_id: int
    machine_id: int
    start_time: datetime
    end_time: datetime
    total_price: float

# Properties to receive on update
class BookingUpdate(BaseModel):
    status: Optional[str] = None
    actual_end_time: Optional[datetime] = None
    start_fuel_level: Optional[float] = None
    end_fuel_level: Optional[float] = None
    start_photos: Optional[List[str]] = None
    end_photos: Optional[List[str]] = None

# Specific schemas for operations
class BookingCheckIn(BaseModel):
    start_fuel_level: float
    start_photos: List[str]

class BookingCheckOut(BaseModel):
    end_fuel_level: float
    end_photos: List[str]

# Properties to return to client
class Booking(BookingBase):
    id: int
    user_id: int
    machine_id: int
    actual_end_time: Optional[datetime] = None
    start_fuel_level: Optional[float] = None
    end_fuel_level: Optional[float] = None
    start_photos: Optional[List[str]] = None
    end_photos: Optional[List[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
