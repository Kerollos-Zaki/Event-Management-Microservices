from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, time

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@user-db:5432/userdb")

# Retry DB connection on startup
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

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="attendee")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="User Service")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "attendee"

@app.post("/users/register")
def register(user: UserCreate):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "role": db_user.role}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "role": user.role}

@app.get("/health")
def health():
    return {"status": "ok", "service": "user-service"}
