# app/api/endpoints/appointment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
from app.db.database import get_db
from app.models.appointment import Appointment
from app.models.offline_appointment import OfflineAppointment
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentReschedule,
    AppointmentStatusUpdate
)
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import RoleEnum, AppointmentStatusEnum
from app.services.availability import is_doctor_available
from app.api.endpoints.websocket import notify_slot_change

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment (Patient only)"""
    if current_user.role != RoleEnum.PATIENT:
        raise HTTPException(status_code=403, detail="Only patients can book appointments")

    # Calculate time window (30-min default duration)
    start_time = appointment.scheduled_at
    end_time = start_time + timedelta(minutes=30)
    
    # Check doctor availability (online + offline)
    if not is_doctor_available(appointment.doctor_id, start_time, end_time, db):
        raise HTTPException(
            status_code=400,
            detail="Doctor not available at this time"
        )

    # Create appointment with calculated end time
    db_appointment = Appointment(
        **appointment.model_dump(),
        patient_id=current_user.id,
        end_time=end_time,
        status=AppointmentStatusEnum.PENDING
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Notify real-time subscribers
    notify_slot_change(appointment.doctor_id)
    
    return db_appointment

@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an appointment (Patient only)"""
    appointment = db.query(Appointment).get(appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own appointments"
        )
    
    if appointment.status != AppointmentStatusEnum.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending appointments can be cancelled"
        )
    
    appointment.status = AppointmentStatusEnum.CANCELLED
    db.commit()
    db.refresh(appointment)
    
    # Notify real-time subscribers
    notify_slot_change(appointment.doctor_id)
    
    return appointment

@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
async def reschedule_appointment(
    appointment_id: int,
    reschedule_data: AppointmentReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reschedule an appointment (Patient only)"""
    appointment = db.query(Appointment).get(appointment_id)
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only reschedule your own appointments"
        )
    
    if appointment.status != AppointmentStatusEnum.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending appointments can be rescheduled"
        )
    
    # Calculate new time window
    new_start = reschedule_data.scheduled_at
    new_end = new_start + timedelta(minutes=30)
    
    # Check availability for new slot
    if not is_doctor_available(appointment.doctor_id, new_start, new_end, db):
        raise HTTPException(
            status_code=400,
            detail="Doctor not available at the new time"
        )
    
    # Update appointment times
    appointment.scheduled_at = new_start
    appointment.end_time = new_end
    db.commit()
    db.refresh(appointment)
    
    # Notify real-time subscribers
    notify_slot_change(appointment.doctor_id)
    
    return appointment

@router.get("/my-appointments", response_model=List[AppointmentResponse])
async def get_my_appointments(
    status: Optional[AppointmentStatusEnum] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all appointments for current user"""
    query = db.query(Appointment)
    
    if current_user.role == RoleEnum.PATIENT:
        query = query.filter(Appointment.patient_id == current_user.id)
    else:
        query = query.filter(Appointment.doctor_id == current_user.id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    return query.order_by(Appointment.scheduled_at.asc()).all()

@router.get("/slots/{doctor_id}")
async def get_available_slots(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    """Get available slots for a doctor"""
    from datetime import datetime, timedelta

    # Define working hours (e.g., 9 AM to 5 PM)
    working_hours_start = 9
    working_hours_end = 17
    slot_duration_minutes = 30

    # Current date
    current_date = datetime.utcnow().date()

    # Generate all possible slots for the day
    slots = []
    start_time = datetime(current_date.year, current_date.month, current_date.day, working_hours_start)
    while start_time.hour < working_hours_end:
        end_time = start_time + timedelta(minutes=slot_duration_minutes)
        slots.append({"start_time": start_time, "end_time": end_time})
        start_time = end_time

    # Fetch existing appointments for the doctor
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.scheduled_at >= datetime.utcnow()
    ).all()

    # Fetch offline appointments for the doctor
    offline_appointments = db.query(OfflineAppointment).filter(
        OfflineAppointment.doctor_id == doctor_id,
        OfflineAppointment.start_time >= datetime.utcnow()
    ).all()

    # Mark slots as unavailable if overlapping with any appointment
    for slot in slots:
        slot["is_available"] = True
        for appointment in appointments + offline_appointments:
            if (
                slot["start_time"] < appointment.end_time
                and slot["end_time"] > appointment.scheduled_at
            ):
                slot["is_available"] = False
                break

    return slots
