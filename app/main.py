from fastapi import FastAPI
from app.api.endpoints import auth, users, appointment, offline_appointment, sms# Add users import
from app.db.base import Base
from app.db.database import engine
from app.core.config import settings

# Create tables (for development only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="IHMP", version="0.1.0")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)  # Add this line
app.include_router(appointment.router)
app.include_router(offline_appointment.router)


@app.get("/")
def health_check():
    return {"status": "OK", "version": "0.1.0"}
