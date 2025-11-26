from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Booking(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    machine_id = Column(Integer, ForeignKey("machine.id"), nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False) # Expected end time
    actual_end_time = Column(DateTime, nullable=True) # For Call-Off
    
    status = Column(String, default="pending_payment") # pending_payment, confirmed, active, completed, cancelled
    total_price = Column(Float, nullable=False)
    
    # Operations
    start_fuel_level = Column(Float, nullable=True)
    end_fuel_level = Column(Float, nullable=True)
    start_photos = Column(JSON, nullable=True) # List of URLs
    end_photos = Column(JSON, nullable=True) # List of URLs
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationships
    user = relationship("User", backref="bookings")
    machine = relationship("Machine", backref="bookings")
