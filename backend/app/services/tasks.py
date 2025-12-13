from app.services.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.notifications import send_notification
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def send_notification_task(user_id: int, type: str, title: str, message: str, payload: dict = None):
    """
    Background task to send notifications.
    """
    db = SessionLocal()
    try:
        logger.info(f"Processing notification for user {user_id}")
        send_notification(db, user_id, type, title, message, payload)
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
    finally:
        db.close()
