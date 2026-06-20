from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import models, schemas

AVATAR_COLORS = [
    "#E53935", "#8E24AA", "#1E88E5", "#00897B",
    "#FB8C00", "#6D4C41", "#039BE5", "#43A047",
]

def _initials(name: str) -> str:
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()

def _friend_balances(db: Session, friend: models.Friend):
    lent = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.friend_id == friend.id,
        models.Transaction.type == "lent"
    ).scalar() or 0.0
    borrowed = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.friend_id == friend.id,
        models.Transaction.type == "borrowed"
    ).scalar() or 0.0
    return lent, borrowed

# ── Friends ───────────────────────────────────────────────────────────────────

def get_friends(db: Session):
    friends = db.query(models.Friend).all()
    result = []
    for f in friends:
        lent, borrowed = _friend_balances(db, f)
        out = schemas.FriendOut(
            id=f.id, name=f.name, phone=f.phone, notes=f.notes,
            avatar_initials=f.avatar_initials, avatar_color=f.avatar_color,
            total_lent=lent, total_borrowed=borrowed, balance=lent - borrowed,
            created_at=f.created_at
        )
        result.append(out)
    return result

def create_friend(db: Session, data: schemas.FriendCreate):
    count = db.query(func.count(models.Friend.id)).scalar()
    color = AVATAR_COLORS[count % len(AVATAR_COLORS)]
    friend = models.Friend(
        name=data.name,
        phone=data.phone,
        notes=data.notes,
        avatar_initials=_initials(data.name),
        avatar_color=data.avatar_color or color,
    )
    db.add(friend)
    db.commit()
    db.refresh(friend)
    lent, borrowed = _friend_balances(db, friend)
    return schemas.FriendOut(
        id=friend.id, name=friend.name, phone=friend.phone, notes=friend.notes,
        avatar_initials=friend.avatar_initials, avatar_color=friend.avatar_color,
        total_lent=lent, total_borrowed=borrowed, balance=lent - borrowed,
        created_at=friend.created_at
    )

def get_friend_detail(db: Session, friend_id: int):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id).first()
    if not friend:
        return None
    lent, borrowed = _friend_balances(db, friend)
    txs = db.query(models.Transaction).filter(
        models.Transaction.friend_id == friend_id
    ).order_by(models.Transaction.date.desc()).all()
    tx_out = [_tx_to_schema(db, t) for t in txs]
    return schemas.FriendDetail(
        id=friend.id, name=friend.name, phone=friend.phone, notes=friend.notes,
        avatar_initials=friend.avatar_initials, avatar_color=friend.avatar_color,
        total_lent=lent, total_borrowed=borrowed, balance=lent - borrowed,
        created_at=friend.created_at, transactions=tx_out
    )

def update_friend(db: Session, friend_id: int, data: schemas.FriendCreate):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id).first()
    if not friend:
        return None
    friend.name = data.name
    friend.phone = data.phone
    friend.notes = data.notes
    friend.avatar_initials = _initials(data.name)
    if data.avatar_color:
        friend.avatar_color = data.avatar_color
    db.commit()
    db.refresh(friend)
    lent, borrowed = _friend_balances(db, friend)
    return schemas.FriendOut(
        id=friend.id, name=friend.name, phone=friend.phone, notes=friend.notes,
        avatar_initials=friend.avatar_initials, avatar_color=friend.avatar_color,
        total_lent=lent, total_borrowed=borrowed, balance=lent - borrowed,
        created_at=friend.created_at
    )

def delete_friend(db: Session, friend_id: int):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id).first()
    if friend:
        db.delete(friend)
        db.commit()

# ── Transactions ──────────────────────────────────────────────────────────────

def _tx_to_schema(db: Session, t: models.Transaction) -> schemas.TransactionOut:
    friend = db.query(models.Friend).filter(models.Friend.id == t.friend_id).first()
    return schemas.TransactionOut(
        id=t.id, friend_id=t.friend_id,
        friend_name=friend.name if friend else None,
        type=t.type, amount=t.amount,
        description=t.description, date=t.date, created_at=t.created_at
    )

def get_transactions(db: Session, friend_id=None, type=None):
    q = db.query(models.Transaction)
    if friend_id:
        q = q.filter(models.Transaction.friend_id == friend_id)
    if type:
        q = q.filter(models.Transaction.type == type)
    txs = q.order_by(models.Transaction.date.desc()).all()
    return [_tx_to_schema(db, t) for t in txs]

def create_transaction(db: Session, data: schemas.TransactionCreate):
    tx = models.Transaction(
        friend_id=data.friend_id,
        type=data.type,
        amount=data.amount,
        description=data.description,
        date=data.date or datetime.utcnow(),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return _tx_to_schema(db, tx)

def update_transaction(db: Session, tx_id: int, data: schemas.TransactionCreate):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if not tx:
        return None
    tx.friend_id = data.friend_id
    tx.type = data.type
    tx.amount = data.amount
    tx.description = data.description
    if data.date:
        tx.date = data.date
    db.commit()
    db.refresh(tx)
    return _tx_to_schema(db, tx)

def delete_transaction(db: Session, tx_id: int):
    tx = db.query(models.Transaction).filter(models.Transaction.id == tx_id).first()
    if tx:
        db.delete(tx)
        db.commit()

# ── Reminders ─────────────────────────────────────────────────────────────────

def _reminder_to_schema(db: Session, r: models.Reminder) -> schemas.ReminderOut:
    friend = db.query(models.Friend).filter(models.Friend.id == r.friend_id).first()
    return schemas.ReminderOut(
        id=r.id, friend_id=r.friend_id,
        friend_name=friend.name if friend else None,
        friend_avatar_initials=friend.avatar_initials if friend else None,
        friend_avatar_color=friend.avatar_color if friend else None,
        message=r.message, remind_at=r.remind_at,
        status=r.status, created_at=r.created_at
    )

def get_reminders(db: Session, status=None):
    q = db.query(models.Reminder)
    if status:
        q = q.filter(models.Reminder.status == status)
    reminders = q.order_by(models.Reminder.remind_at.asc()).all()
    return [_reminder_to_schema(db, r) for r in reminders]

def create_reminder(db: Session, data: schemas.ReminderCreate):
    r = models.Reminder(
        friend_id=data.friend_id,
        message=data.message,
        remind_at=data.remind_at,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _reminder_to_schema(db, r)

def update_reminder(db: Session, reminder_id: int, data: schemas.ReminderCreate):
    r = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not r:
        return None
    r.friend_id = data.friend_id
    r.message = data.message
    r.remind_at = data.remind_at
    db.commit()
    db.refresh(r)
    return _reminder_to_schema(db, r)

def delete_reminder(db: Session, reminder_id: int):
    r = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if r:
        db.delete(r)
        db.commit()

def complete_reminder(db: Session, reminder_id: int):
    r = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if r:
        r.status = "completed"
        db.commit()
        db.refresh(r)
        return _reminder_to_schema(db, r)
    return None

# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_dashboard(db: Session):
    to_receive = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.type == "lent"
    ).scalar() or 0.0
    to_pay = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.type == "borrowed"
    ).scalar() or 0.0
    total_friends = db.query(func.count(models.Friend.id)).scalar()
    recent = db.query(models.Transaction).order_by(
        models.Transaction.date.desc()
    ).limit(10).all()
    return schemas.Dashboard(
        total_to_receive=to_receive,
        total_to_pay=to_pay,
        net_balance=to_receive - to_pay,
        total_friends=total_friends,
        recent_transactions=[_tx_to_schema(db, t) for t in recent]
    )

# ── Export ────────────────────────────────────────────────────────────────────

def export_all(db: Session):
    friends = db.query(models.Friend).all()
    transactions = db.query(models.Transaction).all()
    reminders = db.query(models.Reminder).all()
    return {
        "exported_at": datetime.utcnow().isoformat(),
        "friends": [{"id": f.id, "name": f.name, "phone": f.phone, "notes": f.notes} for f in friends],
        "transactions": [
            {"id": t.id, "friend_id": t.friend_id, "type": t.type,
             "amount": t.amount, "description": t.description, "date": t.date.isoformat()}
            for t in transactions
        ],
        "reminders": [
            {"id": r.id, "friend_id": r.friend_id, "message": r.message,
             "remind_at": r.remind_at.isoformat(), "status": r.status}
            for r in reminders
        ]
    }
