from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.core.config import AppointmentStatusEnum

class AppointmentCreate(BaseModel):
    doctor_id: int
    scheduled_at: datetime

class AppointmentReschedule(BaseModel):
    scheduled_at: datetime

class AppointmentStatusUpdate(BaseModel):
    """Schema for updating appointment status."""
    status: AppointmentStatusEnum

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    status: AppointmentStatusEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
