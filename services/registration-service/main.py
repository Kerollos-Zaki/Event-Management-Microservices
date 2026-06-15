from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import httpx, os, time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@registration-db:5432/registrationdb")
EVENT_SERVICE_URL = os.getenv("EVENT_SERVICE_URL", "http://event-service:8000")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000")

for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        break
    except Exception:
        print(f"DB not ready, retrying ({i+1}/10)...")
        time.sleep(3)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Registration(Base):
    __tablename__ = "registrations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    event_id = Column(Integer)
    status = Column(String, default="confirmed")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Registration Service")

class RegistrationCreate(BaseModel):
    user_id: int
    event_id: int

@app.post("/registrations")
def register(reg: RegistrationCreate):
    try:
        response = httpx.get(f"{EVENT_SERVICE_URL}/events/{reg.event_id}", timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Event not found")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Event service unavailable")

    db = SessionLocal()
    db_reg = Registration(**reg.dict())
    db.add(db_reg)
    db.commit()
    db.refresh(db_reg)

    try:
        httpx.post(f"{NOTIFICATION_SERVICE_URL}/notify", json={
            "user_id": reg.user_id,
            "message": f"You are registered for event ID {reg.event_id}"
        }, timeout=5)
    except Exception:
        pass  # Don't fail registration if notification fails

    return {"id": db_reg.id, "user_id": db_reg.user_id, "event_id": db_reg.event_id, "status": db_reg.status}

@app.get("/registrations/user/{user_id}")
def get_user_registrations(user_id: int):
    db = SessionLocal()
    regs = db.query(Registration).filter(Registration.user_id == user_id).all()
    return [{"id": r.id, "event_id": r.event_id, "status": r.status} for r in regs]

@app.get("/health")
def health():
    return {"status": "ok", "service": "registration-service"}
