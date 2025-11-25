from app.db.base_class import Base
# Import all models here for Alembic
from app.models.user import User
from app.models.machine import Machine
from app.models.availability import AvailabilitySlot
from app.models.offer import Offer
from app.models.watchlist import Watchlist
from app.models.notification import Notification
