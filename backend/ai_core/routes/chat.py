"""
API Routes for chat functionality
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ai_core.ai_handler import ai_assistant
from ai_core.logger import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    flagged: bool
    conversation_id: Optional[str] = None
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    """
    Main chat endpoint
    Receives user message and returns AI response
    """
    try:
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        session_id = chat_request.session_id or "anonymous"
        
        logger.info(f"Chat request from session: {session_id}")
        
        # Generate AI response
        result = await ai_assistant.generate_response(
            chat_request.message,
            session_id
        )
        
        return ChatResponse(
            response=result["response"],
            flagged=result.get("flagged", False),
            conversation_id=result.get("conversation_id"),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat"}
