"""
Magic System Prompts for AI Agents
Provides professional-grade prompts for perfect agent responses
"""
from typing import Dict, Any, Optional


class SystemPromptManager:
    """Manages magic system prompts for all agents"""

    @staticmethod
    def get_agent_prompt(
        agent_name: str,
        user_context: Optional[Dict[str, Any]] = None,
        business_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get magic system prompt for specified agent"""
        prompts = {
            "product_manager": "You are Alex, an elite Product Manager AI agent.",
            "finance_manager": "You are Marcus, an expert Finance Manager AI agent.",
            "marketing_strategist": "You are Ryan, a creative Marketing Strategist AI agent.",
            "leadgen_scraper": "You are Jake, a Lead Generation specialist AI agent.",
            "outbound_emailer": "You are Chris, an Outbound Email specialist AI agent.",
            "booking_callprep": "You are Daniel, a Call Prep and Booking AI agent.",
            "engineer": "You are Kevin, a Senior Software Engineer AI agent.",
            "personal_assistant": "You are Sophia, the Personal AI Assistant with full context awareness.",
        }
        return prompts.get(agent_name, "You are a helpful AI assistant.")


# Global instance
system_prompt_manager = SystemPromptManager()
