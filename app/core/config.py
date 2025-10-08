from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Fashion Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database - Use environment variable, fallback to safe placeholder
    DATABASE_URL: str = "postgresql://CHANGE_ME:CHANGE_ME@localhost/fashion_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security - Use environment variable, fallback to safe placeholder
    SECRET_KEY: str = "CHANGE_THIS_IN_ENV_FILE_USE_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
