from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.booking import Booking
from app.models.transaction import Transaction
from app.models.machine import Machine

def get_financial_metrics(db: Session) -> Dict[str, Any]:
    """
    Get financial metrics.
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

def get_machine_metrics(db: Session) -> Dict[str, Any]:
    """
    Get machine utilization metrics.
    - Top rented machines
    """
    # Total bookings per machine
    top_machines = db.query(
        Machine.name, func.count(Booking.id).label("total_bookings")
    ).join(Booking).group_by(Machine.id).order_by(func.count(Booking.id).desc()).limit(5).all()
    
    return {
        "top_machines": [{"name": m[0], "bookings": m[1]} for m in top_machines]
    }
