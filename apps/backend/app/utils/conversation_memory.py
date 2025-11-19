"""
Conversation Memory System
Stores and retrieves conversation history for agents
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.database import supabase_client
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history storage and retrieval"""

    def __init__(self, max_context_messages: int = 10):
        self.max_context_messages = max_context_messages

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a message to conversation history"""
        message_record = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "agent_name": agent_name,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        try:
            result = supabase_client.table("conversation_messages").insert(message_record).execute()
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            return None

    async def get_conversation_context(
        self,
        conversation_id: str,
        include_system: bool = False
    ) -> List[Dict[str, str]]:
        """Get recent conversation messages for context"""
        try:
            query = supabase_client.table("conversation_messages") \
                .select("role, content") \
                .eq("conversation_id", conversation_id) \
                .order("created_at", desc=False) \
                .limit(self.max_context_messages)
            
            result = query.execute()
            
            messages = []
            for msg in result.data:
                if not include_system and msg["role"] == "system":
                    continue
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return messages
        except Exception as e:
            logger.error(f"Failed to get conversation context for {conversation_id}: {e}")
            return []


# Global instance
conversation_memory = ConversationMemory()
