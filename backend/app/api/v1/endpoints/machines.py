from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.models.machine import Machine
from app.schemas.machine import Machine as MachineSchema, MachineCreate, MachineUpdate
from app.models.user import User
from app.schemas.availability import AvailabilitySlot as AvailabilitySlotSchema
from app.models.availability import AvailabilitySlot as AvailabilitySlotModel
from app.utils.scheduler import generate_slots_for_machine
from datetime import datetime

from app.services import machine as machine_service
from app.core.cache import get_cache, set_cache
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/", response_model=List[MachineSchema])
async def read_machines(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    serial_number: Optional[str] = None,
) -> Any:
    """
    Retrieve machines.
    """
    cache_key = f"machines:{skip}:{limit}:{status}:{serial_number}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    machines = machine_service.get_machines(db, skip, limit, status, serial_number)
    data = jsonable_encoder(machines)
    set_cache(cache_key, data, ttl=60)
    return machines

@router.post("/", response_model=MachineSchema)
def create_machine(
    *,
    db: Session = Depends(deps.get_db),
    machine_in: MachineCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new machine. Only superusers can create machines.
    """
    return machine_service.create_machine(db, machine_in)

@router.get("/{id}", response_model=MachineSchema)
async def read_machine(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get machine by ID.
    """
    machine = machine_service.get_machine(db, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine

@router.put("/{id}", response_model=MachineSchema)
def update_machine(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    machine_in: MachineUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a machine. Only superusers.
    """
    machine = machine_service.get_machine(db, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return machine_service.update_machine(db, machine, machine_in)

@router.delete("/{id}", response_model=MachineSchema)
def delete_machine(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a machine. Only superusers.
    """
    machine = machine_service.get_machine(db, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine_service.delete_machine(db, machine)

@router.post("/{id}/availability/generate", response_model=dict)
def generate_machine_availability(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    days: int = 30,
    start_hour: int = 8,
    end_hour: int = 18,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Generate availability slots for a machine. Only superusers.
    """
    machine = machine_service.get_machine(db, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    slots_count = machine_service.generate_availability(db, id, days, start_hour, end_hour)
    return {"message": f"Generated {slots_count} slots for machine {id}"}

@router.get("/{id}/availability", response_model=List[AvailabilitySlotSchema])
async def read_machine_availability(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get availability slots for a machine.
    """
    machine = machine_service.get_machine(db, id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    return machine_service.get_availability(db, id, start_date, end_date)
