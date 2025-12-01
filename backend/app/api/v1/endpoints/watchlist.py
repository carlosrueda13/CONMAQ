from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.watchlist import Watchlist as WatchlistSchema, WatchlistCreate
from app.services.watchlist import toggle_watchlist_for_user, get_user_watchlist

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
    return toggle_watchlist_for_user(db, current_user, watchlist_in)

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
    return get_user_watchlist(db, current_user, skip, limit)
