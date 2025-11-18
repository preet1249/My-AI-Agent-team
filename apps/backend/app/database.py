"""
Supabase Database Client Configuration
"""
from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

@lru_cache()
def get_supabase() -> Client:
    """
    Get Supabase client instance (cached)

    Returns:
        Supabase client with service_role access
    """
    try:
        supabase: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY  # Use service_role key for backend
        )
        logger.info("Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise

# Global instance
supabase_client = get_supabase()
