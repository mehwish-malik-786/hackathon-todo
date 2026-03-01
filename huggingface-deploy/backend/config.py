from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Production-ready configuration with support for:
    - Database connection
    - CORS configuration
    - HuggingFace API
    - AI model settings
    """

    # Database
    database_url: str

    # API Configuration
    api_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    # HuggingFace API (Phase III)
    hf_token: Optional[str] = None
    hf_model_id: str = "Qwen/Qwen2.5-0.5B-Instruct"
    hf_api_timeout: int = 30

    # AI Configuration
    max_conversation_history: int = 50
    ai_max_retries: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env

    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def is_hf_api_enabled(self) -> bool:
        """Check if HuggingFace API is configured."""
        return bool(self.hf_token)

    def get_hf_model_id(self) -> str:
        """Get HuggingFace model ID with default fallback."""
        return self.hf_model_id or "Qwen/Qwen2.5-0.5B-Instruct"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
