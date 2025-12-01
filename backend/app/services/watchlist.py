from typing import List, Any, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate

def toggle_watchlist_for_user(
    db: Session, current_user: User, watchlist_in: WatchlistCreate
) -> Dict[str, Any]:
    """
    Toggle a machine in the user's watchlist.
    Returns a dictionary with the status ('added' or 'removed') and the machine_id.
    """
    existing_item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.machine_id == watchlist_in.machine_id
    ).first()

    if existing_item:
        db.delete(existing_item)
        db.commit()
        return {"status": "removed", "machine_id": watchlist_in.machine_id}
    else:
        new_item = Watchlist(
            user_id=current_user.id,
            machine_id=watchlist_in.machine_id
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {"status": "added", "machine_id": watchlist_in.machine_id}

def get_user_watchlist(
    db: Session, current_user: User, skip: int = 0, limit: int = 100
) -> List[Watchlist]:
    """
    Retrieve current user's watchlist.
    """
    return db.query(Watchlist).filter(Watchlist.user_id == current_user.id).offset(skip).limit(limit).all()
