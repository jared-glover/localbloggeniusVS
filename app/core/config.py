from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LocalBlogGenius"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for generating localized blog content"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Next.js default
        "http://localhost:8000",  # FastAPI default
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent.parent}/sql_app.db"
    )
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"  # Default model
    MAX_TOKENS: int = 2000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Cache Settings
    CACHE_TTL: int = 60 * 60  # 1 hour in seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Global Settings Instance
settings = Settings()

# Validate OpenAI API Key
if not settings.OPENAI_API_KEY:
    import warnings
    warnings.warn(
        "OPENAI_API_KEY is not set in environment variables. "
        "AI-powered features will not work."
    ) 