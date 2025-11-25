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
