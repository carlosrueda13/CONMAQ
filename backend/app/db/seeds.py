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

def seed_machines(db: Session, count: int = 5) -> list[Machine]:
    logger.info("Seeding 5 specific machines...")
    
    machines_data = [
        {
            "name": "Excavadora CAT 320",
            "serial_number": "CAT320-001",
            "description": "Excavadora de alto rendimiento para construcción pesada.",
            "specs": {"weight": "22t", "power": "150hp", "year": 2022},
            "price_base_per_hour": 150.0,
            "location_lat": 4.6097,
            "location_lng": -74.0817,
            "address": "Bogotá, Colombia",
            "photos": ["https://s7d2.scene7.com/is/image/Caterpillar/CM20200916-5d866-02639"],
            "status": "active",
            "min_hours": 4,
            "capacity_m3h": 120.0,
            "fuel_type": "Diesel",
            "tank_capacity": 300.0
        },
        {
            "name": "Retroexcavadora JCB 3CX",
            "serial_number": "JCB3CX-002",
            "description": None,
            "specs": None,
            "price_base_per_hour": 120.0,
            "location_lat": None,
            "location_lng": None,
            "address": None,
            "photos": None,
            "status": "active",
            "min_hours": 1,
            "capacity_m3h": None,
            "fuel_type": None,
            "tank_capacity": None
        },
        {
            "name": "Grúa Torre Liebherr",
            "serial_number": "LIEB-003",
            "description": "Grúa torre para edificación vertical.",
            "specs": {"max_load": "5t"},
            "price_base_per_hour": 300.0,
            "location_lat": 6.2442,
            "location_lng": -75.5812,
            "address": "Medellín, Antioquia",
            "photos": [],
            "status": "maintenance",
            "min_hours": 8,
            "capacity_m3h": None,
            "fuel_type": "Electric",
            "tank_capacity": None
        },
        {
            "name": "Rodillo Compactador Dynapac",
            "serial_number": "DYN-004",
            "description": "Rodillo vibratorio.",
            "specs": {"weight": "10t"},
            "price_base_per_hour": 90.0,
            "location_lat": None,
            "location_lng": None,
            "address": None,
            "photos": None,
            "status": "active",
            "min_hours": 2,
            "capacity_m3h": None,
            "fuel_type": "Diesel",
            "tank_capacity": 150.0
        },
        {
            "name": "Cargador Frontal Komatsu",
            "serial_number": "KOM-005",
            "description": "Cargador frontal WA380.",
            "specs": {"bucket_capacity": "3.5m3"},
            "price_base_per_hour": 180.0,
            "location_lat": 3.4516,
            "location_lng": -76.5320,
            "address": "Cali, Valle del Cauca",
            "photos": None,
            "status": "inactive",
            "min_hours": 4,
            "capacity_m3h": 200.0,
            "fuel_type": "Diesel",
            "tank_capacity": 250.0
        }
    ]
    
    machines = []
    for m_data in machines_data:
        machine = Machine(**m_data)
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
    start_date = datetime.now(timezone.utc)
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
                    booking=booking,
                    amount=current_price,
                    status="completed",
                    provider_transaction_id=fake.uuid4(),
                    type="payment"
                )
                db.add(txn)
                
    db.commit()
    logger.info("Seeding completed successfully.")
