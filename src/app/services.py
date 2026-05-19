# app/services.py

import requests
from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from app.models import User, ApiKey, UsageEvent
from app.config import OLLAMA_BASE_URL

class CreditService:
    # Handles credit operations for the SaaS billing
    @staticmethod
    def deduct_credits(session: Session, user: User, amount: int) -> bool:
        if user.credits < amount:
            return False
        
        user.credits -= amount
        session.add(user)
        session.commit()

        return True
    
    @staticmethod
    def refund_credits(session: Session, user: User, amount: int):
        user.credits += amount
        session.add(user)
        session.commit()