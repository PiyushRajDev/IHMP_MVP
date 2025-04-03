from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.models.offline_appointment import OfflineAppointment
from app.schemas.offline_appointment import OfflineAppointmentCreate
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import RoleEnum

router = APIRouter(prefix="/offline-appointments", tags=["offline-appointments"])

@router.post("/", response_model=OfflineAppointmentCreate)
async def create_offline_appointment(
    appointment: OfflineAppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an offline appointment (Doctor only)"""
    if current_user.role != RoleEnum.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can create offline appointments")

    # Check for overlapping appointments
    existing = db.query(OfflineAppointment).filter(
        OfflineAppointment.doctor_id == current_user.id,
        OfflineAppointment.start_time < appointment.end_time,
        OfflineAppointment.end_time > appointment.start_time
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Overlapping appointment exists")

    # Create offline appointment
    db_appointment = OfflineAppointment(
        **appointment.model_dump(),
        doctor_id=current_user.id
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment
