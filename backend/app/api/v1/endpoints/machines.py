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

router = APIRouter()

@router.get("/", response_model=List[MachineSchema])
def read_machines(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    serial_number: Optional[str] = None,
) -> Any:
    """
    Retrieve machines.
    """
    query = db.query(Machine)
    if status:
        query = query.filter(Machine.status == status)
    if serial_number:
        query = query.filter(Machine.serial_number == serial_number)
    machines = query.offset(skip).limit(limit).all()
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
    db_obj = Machine(
        name=machine_in.name,
        serial_number=machine_in.serial_number,
        description=machine_in.description,
        specs=machine_in.specs,
        capacity_m3h=machine_in.capacity_m3h,
        fuel_type=machine_in.fuel_type,
        tank_capacity=machine_in.tank_capacity,
        price_base_per_hour=machine_in.price_base_per_hour,
        min_hours=machine_in.min_hours,
        location_lat=machine_in.location_lat,
        location_lng=machine_in.location_lng,
        address=machine_in.address,
        photos=machine_in.photos,
        status=machine_in.status,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{id}", response_model=MachineSchema)
def read_machine(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Get machine by ID.
    """
    machine = db.query(Machine).filter(Machine.id == id).first()
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
    machine = db.query(Machine).filter(Machine.id == id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    update_data = machine_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(machine, field, value)
        
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine

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
    machine = db.query(Machine).filter(Machine.id == id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(machine)
    db.commit()
    return machine

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
    machine = db.query(Machine).filter(Machine.id == id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    slots_count = generate_slots_for_machine(db, id, datetime.now(), days=days, start_hour=start_hour, end_hour=end_hour)
    return {"message": f"Generated {slots_count} slots for machine {id}"}

@router.get("/{id}/availability", response_model=List[AvailabilitySlotSchema])
def read_machine_availability(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Any:
    """
    Get availability slots for a machine.
    """
    machine = db.query(Machine).filter(Machine.id == id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    query = db.query(AvailabilitySlotModel).filter(AvailabilitySlotModel.machine_id == id)
    
    if start_date:
        query = query.filter(AvailabilitySlotModel.start_time >= start_date)
    if end_date:
        query = query.filter(AvailabilitySlotModel.end_time <= end_date)
        
    slots = query.order_by(AvailabilitySlotModel.start_time).all()
    return slots
