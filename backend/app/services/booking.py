from sqlalchemy.orm import Session
from datetime import datetime
from app.models.booking import Booking
from app.models.offer import Offer
from app.models.availability import AvailabilitySlot
from app.schemas.booking import BookingCreate, BookingCheckIn, BookingCheckOut

def create_booking_from_offer(db: Session, offer_id: int) -> Booking:
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise ValueError("Offer not found")
    
    slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == offer.slot_id).first()
    if not slot:
        raise ValueError("Slot not found")

    # Calculate total price (assuming offer amount is per hour or total? 
    # PRD says 'offered_price_total (o por hora)'. Let's assume amount is total for the slot for simplicity in MVP)
    # Actually, slot has start/end time.
    
    booking = Booking(
        user_id=offer.user_id,
        machine_id=slot.machine_id,
        start_time=slot.start_time,
        end_time=slot.end_time,
        total_price=offer.amount, # Assuming offer amount is the winning price
        status="confirmed" # Skipping pending_payment for MVP simplicity or assuming pre-auth
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def perform_check_in(db: Session, booking_id: int, data: BookingCheckIn) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise ValueError("Booking not found")
    
    booking.start_fuel_level = data.start_fuel_level
    booking.start_photos = data.start_photos
    booking.status = "active"
    booking.updated_at = datetime.now()
    
    db.commit()
    db.refresh(booking)
    return booking

def perform_check_out(db: Session, booking_id: int, data: BookingCheckOut) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise ValueError("Booking not found")
    
    booking.end_fuel_level = data.end_fuel_level
    booking.end_photos = data.end_photos
    booking.status = "completed"
    booking.updated_at = datetime.now()
    
    db.commit()
    db.refresh(booking)
    return booking

def perform_call_off(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise ValueError("Booking not found")
    
    booking.actual_end_time = datetime.now()
    # Here we could recalculate price if they return early or late
    booking.status = "completed" # Or 'returned', waiting for check-out inspection
    booking.updated_at = datetime.now()
    
    db.commit()
    db.refresh(booking)
    return booking
