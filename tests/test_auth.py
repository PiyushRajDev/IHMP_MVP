from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_doctor():
    response = client.post(
        "/auth/register/doctor",
        json={
            "email": "doctor@ihmp.com",
            "password": "SecurePass123!",
            "full_name": "Dr. Ramesh Kumar",
            "phone_number": "+919876543210",
            "registration_number": "MH/123456"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "doctor@ihmp.com"
