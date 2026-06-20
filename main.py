from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uvicorn
import os

from database import SessionLocal, engine
import models, schemas, crud

# Secret API key - set this in Render environment variables
API_KEY = os.environ.get("UDHAR_API_KEY", "udhar-secret-key-2026")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="UDHAR API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc"}

@app.middleware("http")
async def api_key_middleware(request, call_next):
    if request.method == "HEAD" or request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)

@app.get("/")
def root():
    return {"status": "UDHAR API is running", "version": "1.0.0"}

@app.head("/")
def root_head():
    return {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Friends ──────────────────────────────────────────────────────────────────

@app.get("/friends", response_model=List[schemas.FriendOut])
def list_friends(db: Session = Depends(get_db)):
    return crud.get_friends(db)

@app.post("/friends", response_model=schemas.FriendOut)
def create_friend(friend: schemas.FriendCreate, db: Session = Depends(get_db)):
    return crud.create_friend(db, friend)

@app.get("/friends/{friend_id}", response_model=schemas.FriendDetail)
def get_friend(friend_id: int, db: Session = Depends(get_db)):
    f = crud.get_friend_detail(db, friend_id)
    if not f:
        raise HTTPException(status_code=404, detail="Friend not found")
    return f

@app.put("/friends/{friend_id}", response_model=schemas.FriendOut)
def update_friend(friend_id: int, friend: schemas.FriendCreate, db: Session = Depends(get_db)):
    return crud.update_friend(db, friend_id, friend)

@app.delete("/friends/{friend_id}")
def delete_friend(friend_id: int, db: Session = Depends(get_db)):
    crud.delete_friend(db, friend_id)
    return {"message": "Friend deleted"}

# ── Transactions ──────────────────────────────────────────────────────────────

@app.get("/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(
    friend_id: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_transactions(db, friend_id=friend_id, type=type)

@app.post("/transactions", response_model=schemas.TransactionOut)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, tx)

@app.put("/transactions/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, tx: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.update_transaction(db, tx_id, tx)

@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    crud.delete_transaction(db, tx_id)
    return {"message": "Transaction deleted"}

# ── Reminders ──────────────────────────────────────────────────────────────────

@app.get("/reminders", response_model=List[schemas.ReminderOut])
def list_reminders(status: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_reminders(db, status=status)

@app.post("/reminders", response_model=schemas.ReminderOut)
def create_reminder(reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    return crud.create_reminder(db, reminder)

@app.put("/reminders/{reminder_id}", response_model=schemas.ReminderOut)
def update_reminder(reminder_id: int, reminder: schemas.ReminderCreate, db: Session = Depends(get_db)):
    return crud.update_reminder(db, reminder_id, reminder)

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    crud.delete_reminder(db, reminder_id)
    return {"message": "Reminder deleted"}

@app.patch("/reminders/{reminder_id}/complete")
def complete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    return crud.complete_reminder(db, reminder_id)

# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.get("/dashboard", response_model=schemas.Dashboard)
def get_dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard(db)

@app.delete("/reset")
def reset_all_data(db: Session = Depends(get_db)):
    db.query(models.Reminder).delete()
    db.query(models.Transaction).delete()
    db.query(models.Friend).delete()
    db.commit()
    return {"message": "All data deleted"}

# ── Export ──────────────────────────────────────────────────────────────────────

@app.get("/export")
def export_data(db: Session = Depends(get_db)):
    return crud.export_all(db)

if __name__ == "__main__":
    import os; port = int(os.environ.get("PORT", 8000)); uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
