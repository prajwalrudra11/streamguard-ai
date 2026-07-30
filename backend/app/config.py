"""
StreamGuard AI - Configuration Management
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ── App ──────────────────────────────────────────────
    app_name: str = "StreamGuard AI"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    
    # ── Supabase ─────────────────────────────────────────
    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(default=None, alias="SUPABASE_SERVICE_KEY")
    
    # ── Google Gemini ────────────────────────────────────
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    
    # ── YouTube API (Phase 3) ────────────────────────────
    youtube_client_id: Optional[str] = Field(default=None, alias="YOUTUBE_CLIENT_ID")
    youtube_client_secret: Optional[str] = Field(default=None, alias="YOUTUBE_CLIENT_SECRET")
    youtube_redirect_uri: str = Field(
        default="http://localhost:8000/auth/youtube/callback",
        alias="YOUTUBE_REDIRECT_URI"
    )
    
    # ── Voice Matching ───────────────────────────────────
    voice_match_threshold: float = Field(default=0.70, alias="VOICE_MATCH_THRESHOLD")
    voice_cooldown_seconds: int = Field(default=5, alias="VOICE_COOLDOWN_SECONDS")
    
    # ── Agent Settings ───────────────────────────────────
    moderation_strict_mode: bool = Field(default=False, alias="MODERATION_STRICT_MODE")
    max_queue_size: int = Field(default=500, alias="MAX_QUEUE_SIZE")
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
