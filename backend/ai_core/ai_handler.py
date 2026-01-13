"""
AI Chat Handler - Integrates with OpenAI or other AI services
"""
import openai
from datetime import datetime
from typing import Dict, Optional
from ai_core.config import settings
from ai_core.logger import logger
from ai_core.moderator import moderator
from ai_core.cloud_storage import cloud_storage
import uuid


class AIAssistant:
    """Handles AI chat interactions"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
    
    async def generate_response(self, user_message: str, session_id: str) -> Dict:
        """
        Generate AI response to user message
        Returns: dict with response and metadata
        """
        # Check content moderation
        is_flagged, flag_reason = moderator.check_content(user_message)
        
        if is_flagged:
            logger.warning(f"Message flagged: {flag_reason}")
            
            # Save flagged content
            conversation_id = str(uuid.uuid4())
            flagged_data = {
                "question": user_message,
                "reason": flag_reason,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            }
            cloud_storage.upload_flagged(flagged_data, conversation_id)
            
            return {
                "response": "We cannot answer this question. Your question has been flagged.",
                "flagged": True,
                "reason": flag_reason
            }
        
        # Generate AI response
        try:
            # Using OpenAI as example - replace with your AI service
            response = await self._call_ai_service(user_message)
            
            # Save conversation
            conversation_id = str(uuid.uuid4())
            conversation_data = {
                "id": conversation_id,
                "session_id": session_id,
                "question": user_message,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "flagged": False
            }
            cloud_storage.upload_conversation(conversation_data, conversation_id)
            
            return {
                "response": response,
                "flagged": False,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "error": str(e)
            }
    
    async def _call_ai_service(self, message: str) -> str:
        """Call AI service (OpenAI, etc.)"""
        try:
            # Example using OpenAI - customize for your needs
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Thespis, a helpful AI assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise


# Singleton instance
ai_assistant = AIAssistant()
