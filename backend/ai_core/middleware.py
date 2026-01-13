"""
Middleware configuration
"""
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from ai_core.config import settings
from ai_core.logger import logger


def setup_rate_limiting():
    """Setup rate limiting"""
    limiter = Limiter(key_func=get_remote_address)
    return limiter


async def log_request_middleware(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
