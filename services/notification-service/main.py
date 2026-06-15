from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Notification Service")

notifications_store: List[dict] = []

class Notification(BaseModel):
    user_id: int
    message: str

@app.post("/notify")
def send_notification(notif: Notification):
    entry = {"user_id": notif.user_id, "message": notif.message}
    notifications_store.append(entry)
    print(f"[NOTIFY] User {notif.user_id}: {notif.message}")
    return {"status": "sent", "user_id": notif.user_id, "message": notif.message}

@app.get("/notifications/{user_id}")
def get_notifications(user_id: int):
    return [n for n in notifications_store if n["user_id"] == user_id]

@app.get("/health")
def health():
    return {"status": "ok", "service": "notification-service"}
