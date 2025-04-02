from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.offline_appointment import OfflineAppointment
from app.models.user import User
from app.services.sms_parser import parse_sms

async def handle_sms(db: Session, from_number: str, message: str) -> bool:
    """
    Handle incoming SMS to create offline appointments.
    
    Args:
        db: Database session
        from_number: Doctor's phone number (from SMS)
        message: Raw SMS text
    """
    parsed = parse_sms(message)
    if not parsed:
        return False

    # Get doctor by phone number
    doctor = db.query(User).filter(
        User.phone_number == from_number,
        User.role == "doctor"
    ).first()

    if not doctor:
        print(f"No doctor found with phone: {from_number}")
        return False

    # Check for existing conflicts
    conflict = db.query(OfflineAppointment).filter(
        OfflineAppointment.doctor_id == doctor.id,
        OfflineAppointment.start_time < parsed["end_time"],
        OfflineAppointment.end_time > parsed["start_time"]
    ).first()

    if conflict:
        print(f"Conflict detected for doctor {doctor.id}")
        return False

    # Create offline appointment
    appointment = OfflineAppointment(
        doctor_id=doctor.id,
        start_time=parsed["start_time"],
        end_time=parsed["end_time"],
        reason=parsed["reason"]
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return True
