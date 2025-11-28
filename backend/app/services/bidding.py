from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.offer import Offer
from app.models.availability import AvailabilitySlot
from app.models.user import User
from app.services.notifications import send_notification

# Configuración de reglas de negocio
MIN_INCREMENT = 10.0  # Incremento mínimo de oferta
SOFT_CLOSE_MINUTES = 5  # Minutos antes del cierre para activar soft close
SOFT_CLOSE_EXTENSION = 10 # Minutos a extender si hay oferta en soft close

def place_bid(db: Session, slot_id: int, user_id: int, amount: float, max_bid_amount: float = None):
    """
    Coloca una oferta en un slot de disponibilidad usando lógica de Proxy Bidding.
    Si max_bid_amount es None, se asume que es una oferta manual (max_bid = amount).
    """
    # 1. Validaciones Básicas
    slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    if not slot.is_available:
        raise HTTPException(status_code=400, detail="Slot is not available for bidding")

    # Si no se provee max_bid, es una oferta manual: max_bid = amount
    if max_bid_amount is None:
        max_bid_amount = amount
    
    # Validar consistencia
    if max_bid_amount < amount:
        raise HTTPException(status_code=400, detail="Max bid cannot be lower than the bid amount")

    now = datetime.now(timezone.utc)
    
    # Inicializar tiempo de fin si es la primera oferta
    if not slot.auction_end_time:
        # Por defecto, la subasta dura hasta el inicio del slot (o una regla de negocio específica)
        # Aquí asumiremos que cierra 24h antes del slot o una duración fija si ya empezó.
        # Para simplificar este MVP, si no tiene fecha fin, le ponemos 24h desde ahora.
        slot.auction_end_time = now + timedelta(hours=24)

    if now > slot.auction_end_time:
        raise HTTPException(status_code=400, detail="Auction has ended")

    # Determinar el precio actual a superar
    current_price = slot.current_price if slot.current_price else slot.base_price
    if current_price is None:
        current_price = 0.0

    # Validar que la oferta máxima del usuario sea suficiente para entrar
    # Debe ser mayor que el precio actual + incremento mínimo (a menos que sea la primera oferta)
    min_required_bid = current_price + MIN_INCREMENT if slot.current_price else current_price
    
    # En una oferta manual, 'amount' es lo que el usuario quiere pagar.
    # En proxy, 'max_bid' es el techo.
    # La validación principal es contra el max_bid_amount, que es lo que define si puede ganar.
    if max_bid_amount < min_required_bid:
        raise HTTPException(
            status_code=400, 
            detail=f"Bid too low. Minimum required is {min_required_bid}"
        )

    # 2. Lógica de Proxy Bidding
    # Buscamos si hay un ganador actual
    current_winner_id = slot.winner_id
    
    # Nueva oferta
    new_offer = Offer(
        user_id=user_id,
        slot_id=slot_id,
        amount=amount, 
        max_bid=max_bid_amount,
        status="active"
    )
    db.add(new_offer)
    
    if not current_winner_id:
        # Caso 1: Primera oferta
        slot.winner_id = user_id
        slot.current_price = slot.base_price # El precio se mantiene en el base, pero ya hay ganador
        # Opcional: Podríamos subirlo a base + incremento, pero usualmente empieza en base.
        if slot.current_price is None:
             slot.current_price = amount # Si no había base, el precio es la oferta inicial
        
        # Actualizar estado de la oferta
        new_offer.status = "winning"
        
    else:
        # Caso 2: Ya hay un ganador. Competencia de Proxy Bids.
        # Obtener la oferta ganadora actual (la activa del winner_id)
        current_winning_offer = db.query(Offer).filter(
            Offer.slot_id == slot_id,
            Offer.user_id == current_winner_id,
            Offer.status == "winning"
        ).first()
        
        if not current_winning_offer:
            # Fallback por consistencia, no debería pasar
            slot.winner_id = user_id
            slot.current_price = current_price + MIN_INCREMENT
            new_offer.status = "winning"
        
        else:
            winner_max_bid = current_winning_offer.max_bid
            
            if max_bid_amount > winner_max_bid:
                # Caso 2a: Nuevo usuario supera el max_bid del anterior
                # El precio sube a: max_bid del anterior + incremento (o el max_bid del nuevo si es menor, pero ya validamos que es mayor)
                # Pero no puede exceder el max_bid del nuevo usuario.
                
                new_price = winner_max_bid + MIN_INCREMENT
                if new_price > max_bid_amount:
                    new_price = max_bid_amount
                
                slot.current_price = new_price
                slot.winner_id = user_id
                
                # Actualizar estados
                current_winning_offer.status = "outbid"
                new_offer.status = "winning"
                
                # Notificar al usuario anterior (current_winner_id)
                send_notification(
                    db=db,
                    user_id=current_winner_id,
                    type="outbid",
                    title="Has sido superado",
                    message=f"Tu oferta ha sido superada. El nuevo precio es {new_price}",
                    payload={"slot_id": slot_id, "new_price": new_price}
                )
                # db.add(notification) is handled inside send_notification
                
            elif max_bid_amount == winner_max_bid:
                # Caso 2b: Empate. El primero que llegó (el actual ganador) mantiene la posición.
                # El precio sube al máximo de ambos.
                slot.current_price = winner_max_bid
                new_offer.status = "outbid" # Perdió por empate (llegó tarde)
                # El ganador sigue siendo el mismo, pero paga más (su máximo)
                
            else:
                # Caso 2c: Nuevo usuario NO supera el max_bid del anterior
                # El precio sube para que el ganador actual supere al nuevo retador
                new_price = max_bid_amount + MIN_INCREMENT
                if new_price > winner_max_bid:
                    new_price = winner_max_bid
                
                slot.current_price = new_price
                # El ganador se mantiene
                new_offer.status = "outbid"

    # 3. Soft Close
    # Si la oferta entra en los últimos X minutos, extender el tiempo
    time_remaining = slot.auction_end_time - now
    if time_remaining < timedelta(minutes=SOFT_CLOSE_MINUTES):
        slot.auction_end_time += timedelta(minutes=SOFT_CLOSE_EXTENSION)

    db.commit()
    db.refresh(slot)
    db.refresh(new_offer)
    return slot, new_offer
