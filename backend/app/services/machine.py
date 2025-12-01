from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.machine import Machine
from app.models.availability import AvailabilitySlot as AvailabilitySlotModel
from app.schemas.machine import MachineCreate, MachineUpdate
from app.utils.scheduler import generate_slots_for_machine

def get_machines(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None, 
    serial_number: Optional[str] = None
) -> List[Machine]:
    query = db.query(Machine)
    if status:
        query = query.filter(Machine.status == status)
    if serial_number:
        query = query.filter(Machine.serial_number == serial_number)
    return query.offset(skip).limit(limit).all()

def create_machine(db: Session, machine_in: MachineCreate) -> Machine:
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

def get_machine(db: Session, machine_id: int) -> Optional[Machine]:
    return db.query(Machine).filter(Machine.id == machine_id).first()

def update_machine(db: Session, machine: Machine, machine_in: MachineUpdate) -> Machine:
    update_data = machine_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(machine, field, value)
        
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine

def delete_machine(db: Session, machine: Machine) -> Machine:
    db.delete(machine)
    db.commit()
    return machine

def generate_availability(
    db: Session, 
    machine_id: int, 
    days: int = 30, 
    start_hour: int = 8, 
    end_hour: int = 18
) -> int:
    return generate_slots_for_machine(db, machine_id, datetime.now(), days=days, start_hour=start_hour, end_hour=end_hour)

def get_availability(
    db: Session, 
    machine_id: int, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> List[AvailabilitySlotModel]:
    query = db.query(AvailabilitySlotModel).filter(AvailabilitySlotModel.machine_id == machine_id)
    
    if start_date:
        query = query.filter(AvailabilitySlotModel.start_time >= start_date)
    if end_date:
        query = query.filter(AvailabilitySlotModel.end_time <= end_date)
        
    return query.order_by(AvailabilitySlotModel.start_time).all()
