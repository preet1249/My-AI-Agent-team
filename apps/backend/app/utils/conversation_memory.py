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

    def __init__(self, max_context_messages: int = 15):
        """
        Initialize conversation memory

        Args:
            max_context_messages: Maximum messages to include in context (default 15)
        """
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

    async def create_conversation(
        self,
        user_id: str,
        title: str = "New Chat",
        agent_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new conversation

        Args:
            user_id: User ID
            title: Conversation title
            agent_type: Primary agent for this conversation

        Returns:
            Conversation ID or None if failed
        """
        conversation_record = {
            "user_id": user_id,
            "title": title,
            "agent_type": agent_type,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        try:
            result = supabase_client.table("conversations").insert(conversation_record).execute()
            return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            return None

    async def get_conversations(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get list of conversations for a user

        Args:
            user_id: User ID
            limit: Maximum number of conversations to return

        Returns:
            List of conversation records
        """
        try:
            result = supabase_client.table("conversations") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("updated_at", desc=True) \
                .limit(limit) \
                .execute()

            return result.data
        except Exception as e:
            logger.error(f"Failed to get conversations for user {user_id}: {e}")
            return []

    async def get_conversation(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific conversation with all its messages

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation record with messages or None
        """
        try:
            # Get conversation metadata
            conv_result = supabase_client.table("conversations") \
                .select("*") \
                .eq("id", conversation_id) \
                .execute()

            if not conv_result.data:
                return None

            conversation = conv_result.data[0]

            # Get all messages for this conversation
            msg_result = supabase_client.table("conversation_messages") \
                .select("*") \
                .eq("conversation_id", conversation_id) \
                .order("created_at", desc=False) \
                .execute()

            conversation["messages"] = msg_result.data
            return conversation

        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None

    async def update_conversation(
        self,
        conversation_id: str,
        title: Optional[str] = None
    ) -> bool:
        """
        Update conversation metadata

        Args:
            conversation_id: Conversation ID
            title: New title

        Returns:
            True if successful, False otherwise
        """
        update_data = {
            "updated_at": datetime.utcnow().isoformat()
        }

        if title:
            update_data["title"] = title

        try:
            supabase_client.table("conversations") \
                .update(update_data) \
                .eq("id", conversation_id) \
                .execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {e}")
            return False


# Global instance
conversation_memory = ConversationMemory()
