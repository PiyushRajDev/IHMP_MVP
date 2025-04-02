from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.sql import func
from app.db.base import Base

class OfflineAppointment(Base):
    __tablename__ = "offline_appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    reason = Column(String)  # "Emergency", "Field visit", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
