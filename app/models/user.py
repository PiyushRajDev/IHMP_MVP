from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.config import RoleEnum
from sqlalchemy.orm import relationship  # Add this import

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone_number = Column(String)
    role = Column(Enum(RoleEnum), default=RoleEnum.PATIENT)
    is_active = Column(Boolean, default=True)
    registration_number = Column(String, nullable=True)  # For doctors only
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient_appointments = relationship(
        "Appointment", 
        foreign_keys="[Appointment.patient_id]",
        back_populates="patient"
    )
    
    doctor_appointments = relationship(
        "Appointment",
        foreign_keys="[Appointment.doctor_id]", 
        back_populates="doctor"
    )
