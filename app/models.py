from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)

    status = Column(String, default="trialing")

    created_at = Column(DateTime, default=datetime.utcnow)


class BillingEvent(Base):
    __tablename__ = "billing_events"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, nullable=False)
    subscription_id = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)
    amount = Column(Float)
    timestamp = Column(DateTime)