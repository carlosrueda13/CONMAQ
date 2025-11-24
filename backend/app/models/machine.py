from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum

class MachineStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Machine(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    
    # Technical Specs
    specs = Column(JSON)  # Flexible JSON for various specs
    capacity_m3h = Column(Float)
    fuel_type = Column(String)
    tank_capacity = Column(Float)
    
    # Operational Metrics
    current_engine_hours = Column(Float, default=0.0)
    service_interval_hours = Column(Float, default=500.0)
    
    # Financials
    price_base_per_hour = Column(Float, nullable=False)
    min_hours = Column(Integer, default=1)
    acquisition_cost = Column(Float, default=0.0)
    maintenance_cost_total = Column(Float, default=0.0)
    
    # Location
    location_lat = Column(Float)
    location_lng = Column(Float)
    address = Column(String)
    
    # Media
    photos = Column(JSON)  # List of URLs
    
    # Status
    status = Column(String, default=MachineStatus.ACTIVE)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    availability_slots = relationship("AvailabilitySlot", back_populates="machine", cascade="all, delete-orphan")
