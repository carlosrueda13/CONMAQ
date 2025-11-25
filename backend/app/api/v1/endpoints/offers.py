from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.schemas.offer import Offer, OfferCreate
from app.services.bidding import place_bid
from app.models.offer import Offer as OfferModel

router = APIRouter()

@router.post("/", response_model=Any)
def create_offer(
    *,
    db: Session = Depends(deps.get_db),
    offer_in: OfferCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Place a new bid (offer) on an availability slot.
    """
    try:
        updated_slot = place_bid(
            db=db,
            slot_id=offer_in.slot_id,
            user_id=current_user.id,
            amount=offer_in.amount,
            max_bid_amount=offer_in.max_bid
        )
        return {
            "status": "success",
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
def read_my_offers(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve offers made by the current user.
    """
    offers = db.query(OfferModel).filter(OfferModel.user_id == current_user.id).offset(skip).limit(limit).all()
    return offers

@router.get("/slot/{slot_id}", response_model=List[Offer])
def read_slot_offers(
    slot_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve offers for a specific slot.
    """
    offers = db.query(OfferModel).filter(OfferModel.slot_id == slot_id).order_by(OfferModel.amount.desc()).offset(skip).limit(limit).all()
    return offers
