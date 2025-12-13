from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.notification import Notification as NotificationSchema
from app.services.notifications import get_user_notifications, mark_notification_as_read

router = APIRouter()

@router.get("/", response_model=List[NotificationSchema])
async def read_notifications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user's notifications.
    """
    return get_user_notifications(db, current_user.id, skip, limit)

@router.put("/{id}/read", response_model=NotificationSchema)
def mark_notification_as_read_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Mark a notification as read.
    """
    notification = mark_notification_as_read(db, current_user.id, id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification
