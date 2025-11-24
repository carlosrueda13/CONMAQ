from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class AvailabilitySlot(Base):
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machine.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False, index=True)
    is_available = Column(Boolean, default=True)
    base_price = Column(Float, nullable=True)  # Precio base específico para este slot (opcional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    machine = relationship("Machine", back_populates="availability_slots")
