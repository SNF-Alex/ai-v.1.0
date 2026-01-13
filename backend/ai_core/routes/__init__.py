"""
Routes package initialization
"""
from ai_core.routes.chat import router as chat_router
from ai_core.routes.dev_moderation import router as dev_router

__all__ = ['chat_router', 'dev_router']
