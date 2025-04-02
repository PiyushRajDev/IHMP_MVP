from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional

class AppointmentStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    
class RoleEnum(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://ihmp_user:securepass123@localhost:5432/ihmp_db"
    
    # Security
    SECRET_KEY: str = "your-secure-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # IMC Integration
    IMC_API_KEY: Optional[str] = None
    DEBUG: bool = False
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@ihmp.com"

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str


    class Config:
        env_file = ".env"
        case_sensitive = True

# Single instance of Settings
settings = Settings()
