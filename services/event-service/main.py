from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@event-db:5432/eventdb")

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

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    location = Column(String)
    date = Column(String)
    capacity = Column(Integer)
    organizer_id = Column(Integer)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Event Service")

class EventCreate(BaseModel):
    title: str
    description: str
    location: str
    date: str
    capacity: int
    organizer_id: int

@app.post("/events")
def create_event(event: EventCreate):
    db = SessionLocal()
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return {"id": db_event.id, "title": db_event.title, "location": db_event.location, "date": db_event.date}

@app.get("/events")
def list_events():
    db = SessionLocal()
    events = db.query(Event).all()
    return [{"id": e.id, "title": e.title, "location": e.location, "date": e.date, "capacity": e.capacity} for e in events]

@app.get("/events/{event_id}")
def get_event(event_id: int):
    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"id": event.id, "title": event.title, "location": event.location, "date": event.date, "capacity": event.capacity}

@app.get("/health")
def health():
    return {"status": "ok", "service": "event-service"}
