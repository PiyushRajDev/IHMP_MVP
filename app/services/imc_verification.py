import requests
from fastapi import HTTPException
from app.core.config import settings

async def verify_doctor_registration(registration_number: str):
    """Verify doctor's registration number with IMC API"""
    try:
        # Mock implementation - replace with actual API call
        if settings.DEBUG:
            return True  # Bypass verification in development
            
        response = requests.post(
            "https://api.imc.gov.in/verify",
            headers={"Authorization": f"Bearer {settings.IMC_API_KEY}"},
            json={"registration_number": registration_number},
            timeout=5
        )
        response.raise_for_status()
        
        return response.json().get("is_valid", False)
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"IMC verification failed: {str(e)}"
        )
