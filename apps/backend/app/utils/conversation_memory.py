"""
Conversation Memory Manager - Stores and retrieves conversation context
Enables agents to remember previous messages in a conversation
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database import supabase_client
import logging

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Manages conversation history for context-aware responses
    Stores messages in Supabase and retrieves recent context
    """

    def __init__(self, max_context_messages: int = 10):
        """
        Initialize conversation memory

        Args:
            max_context_messages: Maximum number of previous messages to include in context
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
        """
        Add a message to conversation history

        Args:
            conversation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            agent_name: Which agent sent this (if assistant)
            metadata: Additional message metadata

        Returns:
            Message ID
        """
        try:
            # Create conversations table entry if first message
            # (We'll create a simple conversations table)

            message_record = {
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "agent_name": agent_name,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }

            # Store in a messages table (we'll add this to schema)
            result = supabase_client.table("conversation_messages").insert(message_record).execute()

            if result.data:
                logger.info(f"Message added to conversation {conversation_id}")
                return result.data[0]["id"]

            return None

        except Exception as e:
            logger.error(f"Failed to add message to conversation: {e}")
            return None

    async def get_conversation_context(
        self,
        conversation_id: str,
        include_system: bool = False
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation messages for context

        Args:
            conversation_id: Conversation identifier
            include_system: Whether to include system messages

        Returns:
            List of messages in OpenAI chat format
        """
        try:
            # Get recent messages
            query = supabase_client.table("conversation_messages") \
                .select("*") \
                .eq("conversation_id", conversation_id) \
                .order("created_at", desc=True) \
                .limit(self.max_context_messages)

            result = query.execute()

            if not result.data:
                return []

            # Convert to OpenAI format and reverse (oldest first)
            messages = []
            for msg in reversed(result.data):
                if msg["role"] == "system" and not include_system:
                    continue

                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
            return messages

        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []

    async def get_conversation_summary(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation summary (message count, participants, etc.)

        Args:
            conversation_id: Conversation identifier

        Returns:
            Summary dict or None
        """
        try:
            result = supabase_client.table("conversation_messages") \
                .select("*") \
                .eq("conversation_id", conversation_id) \
                .execute()

            if not result.data:
                return None

            messages = result.data

            # Extract unique agents
            agents = set(msg.get("agent_name") for msg in messages if msg.get("agent_name"))

            return {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "agents_involved": list(agents),
                "first_message_at": messages[-1]["created_at"] if messages else None,
                "last_message_at": messages[0]["created_at"] if messages else None
            }

        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            return None

    async def clear_conversation(
        self,
        conversation_id: str
    ) -> bool:
        """
        Clear all messages in a conversation

        Args:
            conversation_id: Conversation to clear

        Returns:
            Success boolean
        """
        try:
            result = supabase_client.table("conversation_messages") \
                .delete() \
                .eq("conversation_id", conversation_id) \
                .execute()

            logger.info(f"Cleared conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear conversation: {e}")
            return False

    def format_context_for_prompt(
        self,
        messages: List[Dict[str, str]],
        max_chars: int = 3000
    ) -> str:
        """
        Format conversation context as a readable string for prompt injection

        Args:
            messages: List of messages
            max_chars: Maximum characters to include

        Returns:
            Formatted context string
        """
        if not messages:
            return "No previous conversation context."

        context_parts = ["CONVERSATION HISTORY:"]

        total_chars = 0
        for msg in messages:
            role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
            line = f"\n{role_label}: {msg['content']}"

            if total_chars + len(line) > max_chars:
                context_parts.append("\n[Earlier messages truncated...]")
                break

            context_parts.append(line)
            total_chars += len(line)

        return "".join(context_parts)


# Global instance
conversation_memory = ConversationMemory(max_context_messages=10)
