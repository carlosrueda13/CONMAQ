from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class MachineBase(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None
    description: Optional[str] = None
    specs: Optional[Dict[str, Any]] = None
    capacity_m3h: Optional[float] = None
    fuel_type: Optional[str] = None
    tank_capacity: Optional[float] = None
    price_base_per_hour: Optional[float] = None
    min_hours: Optional[int] = 1
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    address: Optional[str] = None
    photos: Optional[List[str]] = None
    status: Optional[str] = "active"

# Properties to receive on creation
class MachineCreate(MachineBase):
    name: str
    serial_number: str
    price_base_per_hour: float

# Properties to receive on update
class MachineUpdate(MachineBase):
    pass

# Properties shared by models stored in DB
class MachineInDBBase(MachineBase):
    id: int
    current_engine_hours: float
    service_interval_hours: float
    acquisition_cost: float
    maintenance_cost_total: float
    created_at: datetime

    model_config = {"from_attributes": True}

# Properties to return to client
class Machine(MachineInDBBase):
    pass

# Properties stored in DB
class MachineInDB(MachineInDBBase):
    pass
