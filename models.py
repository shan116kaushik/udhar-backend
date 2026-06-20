from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    avatar_initials = Column(String, nullable=True)
    avatar_color = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="friend", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="friend", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    friend_id = Column(Integer, ForeignKey("friends.id"), nullable=False)
    type = Column(String, nullable=False)  # "lent" or "borrowed"
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    friend = relationship("Friend", back_populates="transactions")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    friend_id = Column(Integer, ForeignKey("friends.id"), nullable=False)
    message = Column(String, nullable=False)
    remind_at = Column(DateTime, nullable=False)
    status = Column(String, default="pending")  # "pending" or "completed"
    created_at = Column(DateTime, default=datetime.utcnow)

    friend = relationship("Friend", back_populates="reminders")
