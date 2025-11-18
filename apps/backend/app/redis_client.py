"""
Redis/Upstash Client for Task Queue
"""
import redis.asyncio as redis
from functools import lru_cache
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

@lru_cache()
async def get_redis() -> redis.Redis:
    """
    Get Redis client instance

    Returns:
        Async Redis client
    """
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )

        # Test connection
        await client.ping()
        logger.info("Redis client initialized successfully")
        return client

    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

class RedisQueue:
    """Redis-based task queue manager"""

    def __init__(self):
        self.client = None

    async def connect(self):
        """Connect to Redis"""
        self.client = await get_redis()

    async def enqueue(self, queue_name: str, task_data: dict) -> bool:
        """
        Enqueue a task

        Args:
            queue_name: Queue identifier
            task_data: Task payload as dict

        Returns:
            True if successful
        """
        import json

        if not self.client:
            await self.connect()

        try:
            task_json = json.dumps(task_data)
            await self.client.lpush(queue_name, task_json)
            logger.info(f"Enqueued task to {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            return False

    async def dequeue(self, queue_name: str, timeout: int = 30) -> dict:
        """
        Dequeue a task (blocking)

        Args:
            queue_name: Queue identifier
            timeout: Block timeout in seconds

        Returns:
            Task data dict or None
        """
        import json

        if not self.client:
            await self.connect()

        try:
            result = await self.client.brpop(queue_name, timeout=timeout)
            if result:
                _, task_json = result
                return json.loads(task_json)
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue task: {e}")
            return None

    async def get_queue_size(self, queue_name: str) -> int:
        """Get number of items in queue"""
        if not self.client:
            await self.connect()
        return await self.client.llen(queue_name)

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()

# Global queue instance
redis_queue = RedisQueue()
