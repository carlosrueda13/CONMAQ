from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.watchlist import Watchlist
from app.schemas.watchlist import Watchlist as WatchlistSchema, WatchlistCreate

router = APIRouter()

@router.post("/toggle", response_model=Any)
def toggle_watchlist(
    *,
    db: Session = Depends(deps.get_db),
    watchlist_in: WatchlistCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Toggle a machine in the user's watchlist.
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

@router.get("/", response_model=List[WatchlistSchema])
def read_watchlist(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user's watchlist.
    """
    items = db.query(Watchlist).filter(Watchlist.user_id == current_user.id).offset(skip).limit(limit).all()
    return items
