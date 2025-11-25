from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Offer(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("availabilityslot.id"), nullable=False)
    
    amount = Column(Float, nullable=False)  # Monto actual de la oferta
    max_bid = Column(Float, nullable=False) # Monto máximo dispuesto a pagar (Proxy Bidding)
    
    status = Column(String, default="active") # active, outbid, won, lost
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="offers")
    slot = relationship("AvailabilitySlot", back_populates="offers")
