# app/models/availability.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.db.base import Base

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
