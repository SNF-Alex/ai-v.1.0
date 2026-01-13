"""
Logger configuration with Google Cloud Logging integration
"""
import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
from ai_core.config import settings


def setup_logging():
    """Setup logging configuration"""
    logger = logging.getLogger("thespis")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # JSON Formatter
    formatter = jsonlogger.JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        timestamp=True
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Google Cloud Logging (if enabled)
    if settings.GOOGLE_CLOUD_LOGGING_ENABLED and settings.GCP_PROJECT_ID:
        try:
            from google.cloud import logging as cloud_logging
            client = cloud_logging.Client(project=settings.GCP_PROJECT_ID)
            client.setup_logging()
            logger.info("Google Cloud Logging enabled")
        except Exception as e:
            logger.warning(f"Failed to setup Google Cloud Logging: {e}")
    
    return logger


logger = setup_logging()
