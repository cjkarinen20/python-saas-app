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

def _extract_price_id(session_data: dict) -> str | None:
    metadata_price = session_data.get("metadata", {}).get("price_id")
    if metadata_price:
        return metadata_price
    
    line_items = session_data.get("line_items", {})
    items = line_items.get("data") if isinstance(line_items, dict) else None
    
    if items:
        price_obj = items[0].get("price") or {}
        return price_obj.get("id")

def _get_price_id(session_data: dict) -> str | None: 
    price_id = _extract_price_id(session_data)
    if price_id:
        return price_id
    
    session_id = session_data.get("id")
    if not session_id:
        return None
    
    expanded = stripe.checkout.Session.retrieve(
        session_id, expand = ["line_items.data.price"]
    )
    return _extract_price_id(expanded)

def _find_user(session_data: dict, db: Session) -> User | None:
    user_id_raw = session_data.get("client_reference_id")
    email = session_data.get("customer_details", {}).get("email")
    
    user = None
    
    if user_id_raw:
        try:
            user = db.get(User, int(user_id_raw))
        except (TypeError, ValueError):
            user = None
        
    if not user and email:
        statement = select(User).where(User.email == email)
        user = db.exec(statement).first()
        
    return user

def _record_payment(
    db: Session,
    *,
    user: User,
    price_id: str,
    payment_intent_id: str | None, 
    checkout_session_id: str | None, 
    customer_id: str | None,
    amount: int | None,
    status_value: str | None,
):
    payment = Payment(
        user_id = user.id, # Type: ignore[arg-type]
        stripe_customer_id = customer_id or user.stripe_customer_id or "",
        stripe_payment_intent_id = payment_intent_id or checkout_session_id or "",
        stripe_checkout_session_id = checkout_session_id,
        price_id = price_id,
        credits_granted = PRICE_TO_CREDITS[price_id],
        amount = amount or 0,
        currency = "usd",
        status = status_value or "paid"
    )
    db.add(user)
    db.add(payment)
    db.commit()

@router.post("/checkout")
def create_checkout_session(
    payload: dict, user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    if not STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "Stripe secret key not configured.",
        )
        
    price_id = payload.get("price_id")
    success_url = payload.get("success_url") or "http://localhost:3000/dashboard?payment=success"
    cancel_url = payload.get("cancel_url") or "http://localhost:3000/dashboard?payment=cancel"
        
    if price_id not in PRICE_TO_CREDITS:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid price id")
        
    customer_id = user.stripe_customer_id
    checkout_params = {
        "mode": "payment",
        "payment_method_types": ["card"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": str(user.id),
        "metadata": {"price_id": price_id},
    }
        
    if not customer_id:
        customer = stripe.Customer.create(email = user.email)
        customer_id = customer.id
        user.stripe_customer_id = customer_id
        session.add(user)
        session.commit()
        session.refresh(user)
            
    if customer_id:
        checkout_params["customer"] = customer_id
        
    else:
        checkout_params["customer_email"] = user.email
            
    checkout_session = stripe.checkout.Session.create(**checkout_params)
        
    return {"checkout_url": checkout_session.url, "session_id": checkout_session.id}

def handle_checkout_completed(session_data: dict, db: Session):
    price_id = _get_price_id(session_data)
    if not price_id or price_id not in PRICE_TO_CREDITS:
        return
    
    payment_intent_id = session_data.get("payment_intent")
    if payment_intent_id:
        existing = db.exec(
            select(Payment).where(Payment.stripe_payment_intent_id == payment_intent_id)
        ).first()
        if existing:
            return
        
    user = _find_user(session_data, db)
    if not user:
        return
    
    user.credits += PRICE_TO_CREDITS[price_id]
    customer_id = session_data.get("customer")
    
    if customer_id and not user.stripe_customer_id:
        user.stripe_customer_id = customer_id
        
    _record_payment(
        db,
        user = user,
        price_id = price_id,
        payment_intent_id = session_data.get("id"),
        customer_id = customer_id,
        amount = session_data.get("amount_total"),
        status_value = session_data.get("payment_status"),
    )