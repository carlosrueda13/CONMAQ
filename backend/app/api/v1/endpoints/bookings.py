from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.booking import Booking, BookingCreate, BookingCheckIn, BookingCheckOut
from app.models.user import User
from app.models.booking import Booking as BookingModel
from app.services import booking as booking_service

router = APIRouter()

@router.get("/", response_model=List[Booking])
def read_bookings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve bookings.
    """
    if current_user.is_superuser:
        bookings = db.query(BookingModel).offset(skip).limit(limit).all()
    else:
        bookings = db.query(BookingModel).filter(BookingModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return bookings

@router.post("/", response_model=Booking)
def create_booking(
    *,
    db: Session = Depends(deps.get_db),
    booking_in: BookingCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new booking (Admin or internal).
    """
    booking = BookingModel(
        user_id=booking_in.user_id,
        machine_id=booking_in.machine_id,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time,
        total_price=booking_in.total_price,
        status=booking_in.status
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.post("/from-offer/{offer_id}", response_model=Booking)
def create_booking_from_offer(
    *,
    db: Session = Depends(deps.get_db),
    offer_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Convert a winning offer to a booking.
    """
    try:
        booking = booking_service.create_booking_from_offer(db, offer_id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/check-in", response_model=Booking)
def check_in(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    check_in_data: BookingCheckIn,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Perform check-in (start rental).
    """
    try:
        booking = booking_service.perform_check_in(db, id, check_in_data)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/check-out", response_model=Booking)
def check_out(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    check_out_data: BookingCheckOut,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Perform check-out (end rental).
    """
    try:
        booking = booking_service.perform_check_out(db, id, check_out_data)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/call-off", response_model=Booking)
def call_off(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Call-off rental (early return).
    """
    try:
        booking = booking_service.perform_call_off(db, id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
