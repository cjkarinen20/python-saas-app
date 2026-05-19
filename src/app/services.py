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
        
class StoryGenerationService:
    # Handles AI story generation using the Ollama API.
    
    @staticmethod
    def generate_story(prompt: str, style: str = "adventure") -> Dict[str, Any]:
        # Generate story using Ollama; Create the string prompt for the LLM.
        system_prompt = f"""You are a creative storyteller. 
        Generate a complete engaging {style} story based on the user's prompt.
        Requirements:
        - Write a complete story with a beginning, middle, and end.
        - Keep it between 300-800 word.
        - Make it engaging and well-structured. 
        - Match the requested style: {style}.
        
        User prompt: {prompt}
        
        Write a complete story: """
        
        try:
            # Ollama API request
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json = {
                    "model": "gemma3:4b",
                    "prompt": system_prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 2000,   # Max tokens for complete stories.
                        "temperature": 0.8,    # Creative but not too random.
                        "top_k": 40,
                        "top_p": 0.9,
                        "repeat_penalty": 1.1
                    }
                },
                timeout = 120 # 2 minute timeout for generation.
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = f"Ollama API error: {response.status_code}"
                )
            
            result = response.json()
            story = result.get("response", "").strip()
            
            if not story:
                raise HTTPException(
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                    #detail = f"Ollama API error: {response.status_code}"
                    detail = "Failed to generate story - empty response"
                )
            
            # Token count
            tokens_used = len(story.split())
            return {
                "story": story,
                "tokens_used": tokens_used,
                "model_used": "gemma3:4b",
                "style": style
            }
            
        except requests.exceptions.Timeout:
            raise HTTPException(
                status_code = status.HTTP_504_GATEWAY_TIMEOUT,
                detail = "Story generation timed out. Please try again."
            )

        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail = f"Ollama service unavailable: {str(e)}"
            )
        
        @staticmethod
        def log_usage(
            session: Session,
            user: User,
            api_key: ApiKey,
            prompt: str,
            story: str,
            tokens_used: int,
            cost_credits: int
        ):
            usage_event = UsageEvent(
                user_id = user.id,        # type: ignore
                api_key_id = api_key.id,  # type: ignore
                prompt = prompt,
                story = story,
                tokens_used = tokens_used,
                cost_credits = cost_credits
            )
            
            session.add(usage_event)
            session.commit()
            