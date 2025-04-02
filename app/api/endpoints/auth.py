from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
    get_password_hash,
    get_current_user
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserResponse, UserCreate, DoctorCreate
from app.services.imc_verification import verify_doctor_registration  # New import
# app/api/endpoints/auth.py
from app.core.config import RoleEnum  # Add this import
from app.schemas.user import DoctorProfileUpdate
from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, 
            detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token, "refresh")
    return {
        "access_token": create_access_token({"sub": payload["sub"]}),
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        phone_number=user.phone_number,
        role=user.role.value  # Store enum value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/register/doctor", response_model=UserResponse)
async def register_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db)
):
    # Check email uniqueness
    existing_user = db.query(User).filter(User.email == doctor.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Verify medical license (bypass in development)
    if not settings.DEBUG and not await verify_doctor_registration(doctor.registration_number):
        raise HTTPException(status_code=400, detail="Invalid medical license")

    # Create user
    db_user = User(
        email=doctor.email,
        hashed_password=get_password_hash(doctor.password),
        full_name=doctor.full_name,
        phone_number=doctor.phone_number,
        role=RoleEnum.DOCTOR,
        registration_number=doctor.registration_number
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/doctor/profile", response_model=UserResponse)
async def update_doctor_profile(
    profile_data: DoctorProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update profiles"
        )
    
    for key, value in profile_data.model_dump().items():
        if value is not None:
            setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user
@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint"
        )
    
    return db.query(User).all()

@router.post("/register/patient", response_model=UserResponse)
async def register_patient(
    patient: UserCreate, 
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == patient.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Remove explicit role assignment
    db_user = User(
        **patient.model_dump(exclude={"password", "role"}),  # Exclude role here
        hashed_password=get_password_hash(patient.password)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
