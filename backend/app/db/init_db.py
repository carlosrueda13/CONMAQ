from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import base  # noqa: F401
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you wanted to create them here you could use:
    # base.Base.metadata.create_all(bind=db.get_bind())

    user = db.query(User).filter(User.email == "admin@conmaq.com").first()
    if not user:
        user_in = UserCreate(
            email="admin@conmaq.com",
            password="admin",
            full_name="Admin Conmaq",
            is_superuser=True,
        )
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_superuser=user_in.is_superuser,
            is_active=True,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Superuser created: admin@conmaq.com / admin")
    else:
        print("Superuser already exists")
