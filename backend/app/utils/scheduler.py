from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.models.availability import AvailabilitySlot
from app.models.machine import Machine

def generate_slots_for_machine(
    db: Session,
    machine_id: int,
    start_date: datetime,
    days: int = 30,
    start_hour: int = 8,
    end_hour: int = 18
):
    """
    Genera slots de disponibilidad por hora para una máquina específica.
    Por defecto genera slots de 8:00 a 18:00 para los próximos 30 días.
    """
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return None

    slots_created = 0
    current_date = start_date

    for _ in range(days):
        # Generar slots para el día actual desde start_hour hasta end_hour
        for hour in range(start_hour, end_hour):
            slot_start = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(hours=1)

            # Verificar si ya existe un slot para este horario
            existing_slot = db.query(AvailabilitySlot).filter(
                AvailabilitySlot.machine_id == machine_id,
                AvailabilitySlot.start_time == slot_start
            ).first()

            if not existing_slot:
                new_slot = AvailabilitySlot(
                    machine_id=machine_id,
                    start_time=slot_start,
                    end_time=slot_end,
                    is_available=True,
                    base_price=machine.price_base_per_hour # Usar precio base de la máquina por defecto
                )
                db.add(new_slot)
                slots_created += 1
        
        current_date += timedelta(days=1)

    db.commit()
    return slots_created
