from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.sms_handler import handle_sms
from app.db.database import get_db

router = APIRouter(prefix="/sms", tags=["sms"])

@router.post("/webhook", status_code=status.HTTP_201_CREATED)
async def sms_webhook(
    from_number: str, 
    message: str, 
    db: Session = Depends(get_db)
):
    """Handle incoming SMS from Twilio/Vonage."""
    success = await handle_sms(db, from_number, message)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process SMS"
        )
    return {"status": "success"}
