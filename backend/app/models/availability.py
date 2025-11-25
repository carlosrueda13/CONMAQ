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
    offers = relationship("Offer", back_populates="slot", cascade="all, delete-orphan")
    
    # Campos para gestión de subasta
    current_price = Column(Float, nullable=True) # Precio actual de la subasta (highest bid)
    auction_end_time = Column(DateTime(timezone=True), nullable=True) # Tiempo de cierre (puede extenderse por Soft Close)
    winner_id = Column(Integer, ForeignKey("user.id"), nullable=True) # Ganador actual/final
