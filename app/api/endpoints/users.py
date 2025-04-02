from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse  # Import the new schema
router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    return {"user_id": user_id}
