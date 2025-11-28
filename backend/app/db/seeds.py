import logging
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.machine import Machine
from app.models.availability import AvailabilitySlot
from app.models.offer import Offer
from app.models.booking import Booking
from app.models.transaction import Transaction
from app.utils.scheduler import generate_slots_for_machine

fake = Faker()
logger = logging.getLogger(__name__)

def seed_users(db: Session, count: int = 20) -> list[User]:
    users = []
    logger.info(f"Seeding {count} users...")
    for _ in range(count):
        email = fake.unique.email()
        password = "password123"
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=fake.name(),
            phone=fake.phone_number(),
            role="client",
            is_active=True,
        )
        db.add(user)
        users.append(user)
    db.commit()
    return users

def seed_machines(db: Session, count: int = 50) -> list[Machine]:
    machines = []
    logger.info(f"Seeding {count} machines...")
    machine_types = ["Excavator", "Bulldozer", "Crane", "Forklift", "Loader"]
    brands = ["CAT", "Komatsu", "Volvo", "Hitachi", "JCB"]
    
    for _ in range(count):
        m_type = random.choice(machine_types)
        brand = random.choice(brands)
        name = f"{brand} {m_type} {fake.bothify(text='??-###')}"
        
        machine = Machine(
            name=name,
            serial_number=fake.unique.bothify(text='SN-########'),
            specs={
                "year": random.randint(2015, 2023),
                "power": f"{random.randint(100, 500)} HP",
                "weight": f"{random.randint(5000, 20000)} kg"
            },
            price_base_per_hour=round(random.uniform(50.0, 500.0), 2),
            location_lat=float(fake.latitude()),
            location_lng=float(fake.longitude()),
            status="available"
        )
        db.add(machine)
        machines.append(machine)
    db.commit()
    return machines

def seed_data(db: Session) -> None:
    # 1. Users
    users = seed_users(db, 20)
    
    # 2. Machines
    machines = seed_machines(db, 50)
    
    # 3. Availability Slots (Next 30 days)
    logger.info("Generating availability slots...")
    start_date = datetime.now(timezone.utc).date()
    for machine in machines:
        # Generate slots for a random subset of machines to save time/space if needed, 
        # but for 50 machines it's fine to do all.
        generate_slots_for_machine(
            db=db,
            machine_id=machine.id,
            start_date=start_date,
            days=30,
            start_hour=8,
            end_hour=18
        )
    
    # 4. Simulate Bidding and Bookings (Historical/Active)
    # This is a simplified simulation
    logger.info("Simulating auctions and bookings...")
    
    # Get some slots
    slots = db.query(AvailabilitySlot).limit(100).all()
    
    for slot in slots:
        if random.random() < 0.3: # 30% chance of having activity
            # Simulate bids
            num_bids = random.randint(1, 5)
            current_price = slot.base_price
            winner = None
            
            for _ in range(num_bids):
                bidder = random.choice(users)
                bid_amount = current_price + random.uniform(10, 50)
                
                offer = Offer(
                    user_id=bidder.id,
                    slot_id=slot.id,
                    amount=bid_amount,
                    max_bid=bid_amount + random.uniform(0, 100),
                    status="outbid"
                )
                db.add(offer)
                current_price = bid_amount
                winner = bidder
            
            # Update slot status
            slot.current_price = current_price
            slot.winner_id = winner.id
            
            # Mark the last offer as winning
            offer.status = "winning"
            
            # If slot is in the past, convert to booking
            if slot.start_time < datetime.now(timezone.utc):
                offer.status = "won"
                booking = Booking(
                    user_id=winner.id,
                    machine_id=slot.machine_id,
                    start_time=slot.start_time,
                    end_time=slot.end_time,
                    total_price=current_price,
                    status="completed",
                    actual_end_time=slot.end_time
                )
                db.add(booking)
                
                # Add transaction
                txn = Transaction(
                    booking_id=booking.id, # ID won't be available until flush, but let's rely on commit later or flush now
                    amount=current_price,
                    status="completed",
                    provider_transaction_id=fake.uuid4(),
                    type="payment"
                )
                db.add(txn)
                
    db.commit()
    logger.info("Seeding completed successfully.")
