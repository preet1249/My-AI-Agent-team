"""
Configuration Management - All environment variables and settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    """Application settings from environment variables"""

    # ============================================
    # SERVER CONFIGURATION
    # ============================================
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "*"

    # ============================================
    # SUPABASE CONFIGURATION
    # ============================================
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""  # service_role key for backend

    # ============================================
    # REDIS/UPSTASH CONFIGURATION
    # ============================================
    REDIS_URL: str = ""

    # ============================================
    # OPENROUTER CONFIGURATION
    # ============================================
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Model Selection
    PRODUCT_MANAGER_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    FINANCE_MANAGER_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    MARKETING_STRATEGIST_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    LEADGEN_SCRAPER_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    OUTBOUND_EMAILER_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    BOOKING_CALLPREP_MODEL: str = "nvidia/nemotron-4-340b-instruct"
    ENGINEER_MODEL: str = "anthropic/claude-3-haiku"

    # ============================================
    # GMAIL API CONFIGURATION
    # ============================================
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GMAIL_REFRESH_TOKEN: str = ""

    # ============================================
    # SECURITY CONFIGURATION
    # ============================================
    INTERNAL_SIGNING_KEY: str = "change-this-in-production"
    WEBHOOK_SECRET: str = "change-this-in-production"

    # ============================================
    # RATE LIMITS & CONCURRENCY
    # ============================================
    MAX_CONCURRENT_MODEL_CALLS: int = 3
    MAX_CONCURRENT_SCRAPES: int = 4
    GMAIL_MAX_RPM: int = 250

    # ============================================
    # TIMEOUTS (seconds)
    # ============================================
    MODEL_CALL_TIMEOUT: int = 20
    ENGINEER_TIMEOUT: int = 60
    SCRAPE_TIMEOUT: int = 15
    WEBHOOK_ACK_TIMEOUT: int = 1

    # ============================================
    # CACHE TTL (seconds)
    # ============================================
    SCRAPE_CACHE_TTL: int = 86400  # 24 hours
    MODEL_CACHE_TTL: int = 86400   # 24 hours
    DOMAIN_CACHE_TTL: int = 3600   # 1 hour

    # ============================================
    # RETRY CONFIGURATION
    # ============================================
    MAX_RETRIES: int = 3
    RETRY_DELAYS: List[int] = [2, 8, 20]  # Exponential backoff

    # ============================================
    # SCRAPING POLITENESS
    # ============================================
    SCRAPE_DELAY_MIN: int = 2
    SCRAPE_DELAY_MAX: int = 5
    MAX_REQUESTS_PER_DOMAIN_DAILY: int = 200

    # ============================================
    # MONITORING (Optional - Sentry)
    # ============================================
    SENTRY_DSN: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
