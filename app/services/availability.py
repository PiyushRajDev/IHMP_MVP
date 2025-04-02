from datetime import datetime
from sqlalchemy.orm import Session
from app.models.appointment import Appointment
from app.models.offline_appointment import OfflineAppointment

def is_doctor_available(doctor_id: int, start_time: datetime, end_time: datetime, db: Session):
    # Check online appointments
    online_conflict = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.scheduled_at < end_time,
        Appointment.end_time > start_time,
        Appointment.status != "cancelled"
    ).first()
    
    # Check offline appointments
    offline_conflict = db.query(OfflineAppointment).filter(
        OfflineAppointment.doctor_id == doctor_id,
        OfflineAppointment.start_time < end_time,
        OfflineAppointment.end_time > start_time
    ).first()
    
    return not (online_conflict or offline_conflict)
