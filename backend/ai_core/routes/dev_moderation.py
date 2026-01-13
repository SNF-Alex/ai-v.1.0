"""
Developer moderation routes for reviewing and managing conversations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
import json
import random
import string
from datetime import datetime, timedelta
from ai_core.config import settings
from ai_core.logger import logger
from ai_core.email_service import send_verification_code

router = APIRouter()

# Temporary storage for verification codes (in production, use Redis or database)
verification_codes = {}


class EmailVerificationRequest(BaseModel):
    email: EmailStr


class CodeVerificationRequest(BaseModel):
    email: EmailStr
    code: str


class ConversationReview(BaseModel):
    conversation_id: str
    action: str  # "good", "bad", "flagged"


def is_email_allowed(email: str) -> bool:
    """Check if email is in allowed list"""
    try:
        if os.path.exists(settings.ALLOWED_EMAILS_FILE):
            with open(settings.ALLOWED_EMAILS_FILE, 'r') as f:
                allowed_emails = [line.strip().lower() for line in f if line.strip()]
                return email.lower() in allowed_emails
        return False
    except Exception as e:
        logger.error(f"Error checking allowed emails: {e}")
        return False


def generate_verification_code() -> str:
    """Generate 8-digit verification code"""
    return ''.join(random.choices(string.digits, k=8))


@router.post("/verify-email")
async def verify_email(request: EmailVerificationRequest):
    """
    Step 1: Verify email is allowed and send verification code
    """
    if not is_email_allowed(request.email):
        raise HTTPException(status_code=403, detail="Email not authorized")
    
    # Generate and store code
    code = generate_verification_code()
    verification_codes[request.email] = {
        "code": code,
        "expires": datetime.utcnow() + timedelta(minutes=10)
    }
    
    # Send code via email
    try:
        await send_verification_code(request.email, code)
        logger.info(f"Verification code sent to {request.email}")
        return {"message": "Verification code sent", "email": request.email}
    except Exception as e:
        logger.error(f"Failed to send verification code: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification code")


@router.post("/verify-code")
async def verify_code(request: CodeVerificationRequest):
    """
    Step 2: Verify the code entered by user
    """
    if request.email not in verification_codes:
        raise HTTPException(status_code=400, detail="No verification code found")
    
    stored = verification_codes[request.email]
    
    # Check expiration
    if datetime.utcnow() > stored["expires"]:
        del verification_codes[request.email]
        raise HTTPException(status_code=400, detail="Verification code expired")
    
    # Check code
    if stored["code"] != request.code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Code verified successfully
    del verification_codes[request.email]
    logger.info(f"Developer verified: {request.email}")
    
    # In production, generate JWT token here
    return {
        "message": "Verification successful",
        "access_granted": True
    }


@router.get("/conversations")
async def get_conversations():
    """
    Get all conversations for review
    """
    try:
        conversations = []
        conv_path = settings.CONVERSATIONS_PATH
        
        if os.path.exists(conv_path):
            for filename in os.listdir(conv_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(conv_path, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        conv_data = json.load(f)
                        conversations.append(conv_data)
        
        return {"conversations": conversations, "count": len(conversations)}
        
    except Exception as e:
        logger.error(f"Error loading conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to load conversations")


@router.post("/review-conversation")
async def review_conversation(review: ConversationReview):
    """
    Review a conversation and move it to appropriate folder
    """
    try:
        conv_path = settings.CONVERSATIONS_PATH
        source_file = os.path.join(conv_path, f"{review.conversation_id}.json")
        
        if not os.path.exists(source_file):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Read conversation data
        with open(source_file, 'r', encoding='utf-8') as f:
            conv_data = json.load(f)
        
        # Determine destination based on action
        if review.action == "good":
            dest_path = settings.GOOD_RESPONSES_PATH
        elif review.action == "bad":
            dest_path = settings.BAD_RESPONSES_PATH
        elif review.action == "flagged":
            dest_path = settings.FLAGGED_PATH
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        # Create destination directory
        os.makedirs(dest_path, exist_ok=True)
        
        # Move file
        dest_file = os.path.join(dest_path, f"{review.conversation_id}.json")
        os.rename(source_file, dest_file)
        
        logger.info(f"Conversation {review.conversation_id} marked as {review.action}")
        
        return {"message": f"Conversation marked as {review.action}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to review conversation")
