from fastapi.testclient import TestClient
from app.main import app
from app.db.database import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_doctor_registration_flow():
    test_user = {
        "email": "test_doctor@ihmp.com",
        "password": "TestPass123!",
        "full_name": "Dr. Test User",
        "phone_number": "+919876543210",
        "registration_number": "TEST/123"
    }
    
    # Registration
    response = client.post("/auth/register/doctor", json=test_user)
    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]
