"""
Configuration settings for the application
Loads from environment variables and Google Cloud Secret Manager
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Thespis AI")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Google Cloud
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    GCP_BUCKET_NAME: str = os.getenv("GCP_BUCKET_NAME", "")
    SECRET_MANAGER_ENABLED: bool = os.getenv("SECRET_MANAGER_ENABLED", "False").lower() == "true"
    
    # AI Service
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # Email
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@thespis.ai")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", 10))
    
    # Content Moderation
    MODERATION_ENABLED: bool = os.getenv("MODERATION_ENABLED", "True").lower() == "true"
    PROFANITY_FILTER_ENABLED: bool = os.getenv("PROFANITY_FILTER_ENABLED", "True").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    GOOGLE_CLOUD_LOGGING_ENABLED: bool = os.getenv("GOOGLE_CLOUD_LOGGING_ENABLED", "False").lower() == "true"
    
    # Paths
    CONVERSATIONS_PATH: str = "conversations"
    FLAGGED_PATH: str = "flagged_questions"
    GOOD_RESPONSES_PATH: str = "good_responses"
    BAD_RESPONSES_PATH: str = "bad_responses"
    LOGS_PATH: str = "logs"
    ALLOWED_EMAILS_FILE: str = "allowed_emails.txt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
