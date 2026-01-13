"""
Main entry point for Thespis AI Assistant Backend
FastAPI application with Google Cloud integration
"""
import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ai_core.config import settings
from ai_core.routes import chat_router, dev_router
from ai_core.middleware import setup_rate_limiting
from ai_core.logger import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Thespis AI Assistant Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS Origins: {settings.ALLOWED_ORIGINS}")
    yield
    # Shutdown
    logger.info("Shutting down Thespis AI Assistant Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="Thespis AI Assistant API",
    description="Secure backend for AI assistant with Google Cloud integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
limiter = setup_rate_limiting()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(dev_router, prefix="/api/dev", tags=["developer"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Thespis AI Assistant API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=settings.DEBUG
    )
