from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.services.metrics import get_financial_metrics as get_financial_metrics_service
from app.services.metrics import get_machine_metrics as get_machine_metrics_service
from app.core.cache import get_cache, set_cache
from fastapi.encoders import jsonable_encoder

router = APIRouter()

@router.get("/financial")
async def get_financial_metrics(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_admin),
):
    """
    Get financial metrics (Admin only).
    - Total Revenue (from completed transactions)
    - Pending Revenue (from pending bookings)
    """
    cache_key = "metrics:financial"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    metrics = get_financial_metrics_service(db)
    set_cache(cache_key, jsonable_encoder(metrics), ttl=300) # 5 minutes cache
    return metrics

@router.get("/machines")
async def get_machine_metrics(
    db: Session = Depends(deps.get_db),
    current_user: Any = Depends(deps.get_current_active_admin),
):
    """
    Get machine utilization metrics (Admin only).
    - Top rented machines
    - Total hours rented
    """
    cache_key = "metrics:machines"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    metrics = get_machine_metrics_service(db)
    set_cache(cache_key, jsonable_encoder(metrics), ttl=300)
    return metrics
