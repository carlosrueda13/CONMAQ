from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.offer import Offer, OfferCreate
from app.services import offer as offer_service
from app.models.offer import Offer as OfferModel
from app.core.limiter import limiter

router = APIRouter()

@router.post("/", response_model=Any)
@limiter.limit("20/minute")
def create_offer(
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    offer_in: OfferCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Place a new bid (offer) on an availability slot.
    """
    try:
        updated_slot, new_offer = offer_service.place_bid(
            db=db,
            slot_id=offer_in.slot_id,
            user_id=current_user.id,
            amount=offer_in.amount,
            max_bid_amount=offer_in.max_bid
        )
        return {
            "status": "success",
            "offer_id": new_offer.id,
            "slot_id": updated_slot.id,
            "current_price": updated_slot.current_price,
            "winner_id": updated_slot.winner_id,
            "auction_end_time": updated_slot.auction_end_time
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error during bidding")

@router.get("/my-offers", response_model=List[Offer])
async def read_my_offers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve offers made by the current user.
    """
    return offer_service.get_user_offers(db, current_user.id, skip, limit)

@router.get("/slot/{slot_id}", response_model=List[Offer])
async def read_slot_offers(
    slot_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve offers for a specific slot.
    """
    return offer_service.get_slot_offers(db, slot_id, skip, limit)
