"""
Konfigurasi aplikasi EduMindAI
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Settings aplikasi dengan validasi Pydantic"""
    
    # Aplikasi
    APP_NAME: str = "EduMindAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"
    
    # Google Gemini API
    GEMINI_API_KEY: str = Field(..., description="API Key untuk Google Gemini")
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TIMEOUT_SECONDS: int = 30
    GEMINI_RETRY_ATTEMPTS: int = 3
    GEMINI_MAX_CALLS_PER_SESSION: int = 2
    
    # PostgreSQL Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "edumind_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DATABASE_URL: str = ""
    
    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    
    # Keamanan
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Session
    SESSION_TIMEOUT_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Language
    DEFAULT_LANGUAGE: str = "id"
    SUPPORTED_LANGUAGES: List[str] = ["id", "en"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build DATABASE_URL if not provided
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
