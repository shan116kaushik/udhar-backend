from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ── Friend ────────────────────────────────────────────────────────────────────

class FriendCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    notes: Optional[str] = None
    avatar_color: Optional[str] = None

class FriendOut(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    notes: Optional[str]
    avatar_initials: Optional[str]
    avatar_color: Optional[str]
    total_lent: float = 0.0
    total_borrowed: float = 0.0
    balance: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

class FriendDetail(FriendOut):
    transactions: List["TransactionOut"] = []

# ── Transaction ───────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    friend_id: int
    type: str  # "lent" or "borrowed"
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None

class TransactionOut(BaseModel):
    id: int
    friend_id: int
    friend_name: Optional[str] = None
    type: str
    amount: float
    description: Optional[str]
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# ── Reminder ──────────────────────────────────────────────────────────────────

class ReminderCreate(BaseModel):
    friend_id: int
    message: str
    remind_at: datetime

class ReminderOut(BaseModel):
    id: int
    friend_id: int
    friend_name: Optional[str] = None
    friend_avatar_initials: Optional[str] = None
    friend_avatar_color: Optional[str] = None
    message: str
    remind_at: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ── Dashboard ─────────────────────────────────────────────────────────────────

class Dashboard(BaseModel):
    total_to_receive: float
    total_to_pay: float
    net_balance: float
    total_friends: int
    recent_transactions: List[TransactionOut]

FriendDetail.model_rebuild()
