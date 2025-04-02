from datetime import datetime
from pydantic import BaseModel

class OfflineAppointmentCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: str

class OfflineAppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime
    reason: str
    created_at: datetime
