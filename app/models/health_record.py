from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))
    raw_data = Column(Text)  # Original medical data
    summary = Column(Text)   # AI-generated summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
