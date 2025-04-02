from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, object_session
from datetime import timedelta
from app.db.base import Base
from app.core.config import AppointmentStatusEnum

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    scheduled_at = Column(DateTime(timezone=True))  # Single definition
    end_time = Column(DateTime(timezone=True))      # Add this field
    status = Column(Enum(AppointmentStatusEnum), default=AppointmentStatusEnum.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="patient_appointments")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-set end_time if not provided
        if self.scheduled_at and not self.end_time:
            self.end_time = self.scheduled_at + timedelta(minutes=30)
@event.listens_for(Appointment.scheduled_at, 'set')
def update_end_time(target, value, oldvalue, initiator):
    if value and not target.end_time:
        target.end_time = value + timedelta(minutes=30)
    session = object_session(target)
    if session:
        session.add(target)