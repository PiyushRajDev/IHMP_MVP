from pydantic import BaseModel, EmailStr, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from app.core.config import RoleEnum

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.PATIENT

    @model_validator(mode="after")
    def validate_patient_fields(self) -> "UserCreate":
        if self.role == RoleEnum.PATIENT and hasattr(self, "registration_number"):
            raise ValueError("Patients cannot have a registration number.")
        return self

class DoctorCreate(UserBase):
    password: str
    registration_number: str
    role: RoleEnum = RoleEnum.DOCTOR

    @model_validator(mode="after")
    def validate_doctor_fields(self) -> "DoctorCreate":
        if self.role == RoleEnum.DOCTOR and not self.registration_number:
            raise ValueError("Doctors must provide a valid registration number.")
        return self
        
class UserInDB(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    hashed_password: str
    registration_number: Optional[str] = None  # Add this line

    model_config = ConfigDict(
        from_attributes=True,
        exclude={"hashed_password"}  # Proper exclusion syntax for V2
    )

class UserResponse(UserBase):
    id: int
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    registration_number: Optional[str] = None  # Doctor-specific field

    @model_validator(mode="after")
    def exclude_registration_for_patients(self) -> "UserResponse":
        # Exclude registration_number for patients
        if self.role == RoleEnum.PATIENT:
            self.registration_number = None
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "doctor@ihmp.com",
                "full_name": "Dr. Ramesh Kumar",
                "phone_number": "+919876543210",
                "role": "doctor",
                "is_active": True,
                "created_at": "2025-03-18T16:04:05.891593Z",
                "updated_at": None,
                "registration_number": "MH/123456"
            }
        }
    )

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class DoctorProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    registration_number: Optional[str] = None

    @model_validator(mode="after")
    def validate_doctor_profile_fields(self) -> "DoctorProfileUpdate":
        if self.registration_number is None:
            raise ValueError("Registration number cannot be empty for doctors.")
        return self
