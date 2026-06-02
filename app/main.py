from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import Base, engine, SessionLocal
from app.models import Subscription, BillingEvent


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Subscription Service API")


class CreateSubscriptionRequest(BaseModel):
    user_id: str


class BillingWebhookRequest(BaseModel):
    event_id: str
    subscription_id: int
    timestamp: datetime
    amount: float
    event_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/subscriptions")
def create_subscription(request: CreateSubscriptionRequest, db: Session = Depends(get_db)):
    subscription = Subscription(
        user_id=request.user_id,
        status="trialing"
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


@app.get("/subscriptions/{subscription_id}")
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription


@app.post("/subscriptions/{subscription_id}/cancel")
def cancel_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.status = "cancelled"

    db.commit()
    db.refresh(subscription)

    return subscription


@app.post("/webhooks/billing")
def billing_webhook(request: BillingWebhookRequest, db: Session = Depends(get_db)):
    existing_event = db.query(BillingEvent).filter(
        BillingEvent.event_id == request.event_id
    ).first()

    if existing_event is not None:
        return {
            "message": "Event already processed",
            "event_id": request.event_id
        }

    subscription = db.query(Subscription).filter(
        Subscription.id == request.subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(status_code=404, detail="Subscription not found")

    billing_event = BillingEvent(
        event_id=request.event_id,
        subscription_id=request.subscription_id,
        event_type=request.event_type,
        amount=request.amount,
        timestamp=request.timestamp
    )

    db.add(billing_event)

    if subscription.status == "cancelled":
        db.commit()
        return {
            "message": "Subscription already cancelled. Event stored but ignored."
        }

    if request.event_type == "payment.succeeded":
        subscription.status = "active"

    elif request.event_type == "payment.failed":
        if subscription.status == "active":
            subscription.status = "grace"

    else:
        raise HTTPException(status_code=400, detail="Invalid event type")

    db.commit()
    db.refresh(subscription)

    return subscription