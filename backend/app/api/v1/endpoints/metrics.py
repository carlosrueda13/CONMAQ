from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.services.metrics import get_financial_metrics as get_financial_metrics_service
from app.services.metrics import get_machine_metrics as get_machine_metrics_service

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
    return get_financial_metrics_service(db)

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
    return get_machine_metrics_service(db)
