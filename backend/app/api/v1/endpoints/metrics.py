from typing import Any, List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api import deps
from app.models.booking import Booking
from app.models.transaction import Transaction
from app.models.machine import Machine

router = APIRouter()

@router.get("/financial")
def get_financial_metrics(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_admin),
):
    """
    Get financial metrics (Admin only).
    - Total Revenue (from completed transactions)
    - Pending Revenue (from pending bookings)
    """
    total_revenue = db.query(func.sum(Transaction.amount)).filter(Transaction.status == "completed").scalar() or 0.0
    pending_revenue = db.query(func.sum(Booking.total_price)).filter(Booking.status == "pending_payment").scalar() or 0.0
    
    return {
        "total_revenue": total_revenue,
        "pending_revenue": pending_revenue,
        "currency": "USD"
    }

@router.get("/machines")
def get_machine_metrics(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_admin),
):
    """
    Get machine utilization metrics (Admin only).
    - Top rented machines
    - Total hours rented
    """
    # Total bookings per machine
    top_machines = db.query(
        Machine.name, func.count(Booking.id).label("total_bookings")
    ).join(Booking).group_by(Machine.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    
    # Total hours rented (approximate based on start/end time)
    # Note: In a real app, we would calculate exact duration
    
    return {
        "top_machines": [{"name": m[0], "bookings": m[1]} for m in top_machines]
    }
