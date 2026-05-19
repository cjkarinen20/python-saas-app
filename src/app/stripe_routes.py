import stripe 
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.auth import get_current_user
from app.config import (
    PRICE_ID_5,
    PRICE_ID_10,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)   # Stripe keys and price IDs loaded from .env file
from app.database import get_session # DB session dependency
from app.models import Payment, User # ORM models used for crediting users and recording payments

# Configure the global Stripe client
stripe.api_key = STRIPE_SECRET_KEY

# All billing routes live under /billing to keep concerns seperated
router = APIRouter(prefix = "/billing", tags = ["billing"])

PRICE_TO_CREDITS = {
    pid: credits
    for pid, credits in [
        (PRICE_ID_5, 5),
        (PRICE_ID_10, 10),
    ]
    if pid
}