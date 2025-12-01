from sqlalchemy.orm import Session
from app.models.notification import Notification

def send_notification(db: Session, user_id: int, type: str, title: str, message: str, payload: dict = None):
    """
    Create a notification in the DB and simulate sending an email/push.
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        payload=payload
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Mock sending email/push
    print(f"--- MOCK NOTIFICATION SENT ---")
    print(f"To User: {user_id}")
    print(f"Type: {type}")
    print(f"Title: {title}")
    print(f"Message: {message}")
    print(f"------------------------------")
    
    return notification

def get_user_notifications(
    db: Session, current_user_id: int, skip: int = 0, limit: int = 100
) -> list[Notification]:
    """
    Retrieve current user's notifications.
    """
    return db.query(Notification).filter(
        Notification.user_id == current_user_id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notification_as_read(
    db: Session, current_user_id: int, notification_id: int
) -> Notification | None:
    """
    Mark a notification as read. Returns None if not found.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user_id
    ).first()
    
    if not notification:
        return None
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification

