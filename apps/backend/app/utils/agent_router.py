"""
Agent Router - Handles agent-to-agent communication and @mentions
Enables agents to call each other like teammates
"""
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)


# Agent name mapping (human names)
AGENT_NAMES = {
    # Boy names for male agents
    "alex": "product_manager",
    "marcus": "finance_manager",
    "ryan": "marketing_strategist",
    "jake": "leadgen_scraper",
    "chris": "outbound_emailer",
    "daniel": "booking_callprep",
    "kevin": "engineer",

    # Girl name for personal assistant
    "sophia": "personal_assistant",

    # Also support role names
    "product_manager": "product_manager",
    "finance_manager": "finance_manager",
    "marketing_strategist": "marketing_strategist",
    "leadgen_scraper": "leadgen_scraper",
    "outbound_emailer": "outbound_emailer",
    "booking_callprep": "booking_callprep",
    "engineer": "engineer",
    "personal_assistant": "personal_assistant",
    "assistant": "personal_assistant"
}


# Reverse mapping (agent_id -> name)
AGENT_ID_TO_NAME = {
    "product_manager": "Alex",
    "finance_manager": "Marcus",
    "marketing_strategist": "Ryan",
    "leadgen_scraper": "Jake",
    "outbound_emailer": "Chris",
    "booking_callprep": "Daniel",
    "engineer": "Kevin",
    "personal_assistant": "Sophia"
}


# Agent expertise domains (for smart routing)
AGENT_EXPERTISE = {
    "product_manager": ["product", "roadmap", "features", "market", "trends", "insights", "strategy"],
    "finance_manager": ["finance", "budget", "revenue", "expenses", "profit", "cost", "pricing"],
    "marketing_strategist": ["marketing", "campaign", "branding", "audience", "content", "ads"],
    "leadgen_scraper": ["leads", "prospects", "scraping", "data", "research", "contacts"],
    "outbound_emailer": ["email", "outreach", "communication", "messaging", "follow-up"],
    "booking_callprep": ["meetings", "calls", "calendar", "scheduling", "prep", "scripts"],
    "engineer": ["code", "technical", "programming", "development", "bug", "implementation", "api"],
    "personal_assistant": ["task", "schedule", "organize", "manage", "assign", "calendar", "summary"]
}


class AgentRouter:
    """
    Routes messages to appropriate agents and handles agent communication
    """

    def parse_mentions(self, text: str) -> List[str]:
        """
        Extract @mentions from text

        Args:
            text: Message text with @mentions

        Returns:
            List of agent IDs mentioned

        Example:
            "@alex please ask @kevin if this is possible"
            Returns: ["product_manager", "engineer"]
        """
        # Find all @mentions
        mentions = re.findall(r'@(\w+)', text.lower())

        # Convert names to agent IDs
        agent_ids = []
        for mention in mentions:
            agent_id = AGENT_NAMES.get(mention)
            if agent_id and agent_id not in agent_ids:
                agent_ids.append(agent_id)

        return agent_ids

    def detect_agent_needed(self, text: str, current_agent: str = None) -> Optional[str]:
        """
        Detect if another agent should handle this based on keywords

        Args:
            text: User message
            current_agent: Current agent handling request

        Returns:
            Agent ID that should handle this, or None

        Example:
            Text: "How much will this cost?"
            Current: product_manager
            Returns: "finance_manager"
        """
        text_lower = text.lower()

        # Score each agent based on keyword matches
        scores = {}
        for agent_id, keywords in AGENT_EXPERTISE.items():
            # Skip current agent
            if agent_id == current_agent:
                continue

            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[agent_id] = score

        # Return agent with highest score
        if scores:
            best_agent = max(scores, key=scores.get)
            # Only suggest if score is >= 2 (avoid false positives)
            if scores[best_agent] >= 2:
                return best_agent

        return None

    def format_agent_request(
        self,
        from_agent: str,
        to_agent: str,
        question: str
    ) -> str:
        """
        Format a request from one agent to another

        Args:
            from_agent: Requesting agent ID
            to_agent: Target agent ID
            question: Question to ask

        Returns:
            Formatted prompt for target agent
        """
        from_name = AGENT_ID_TO_NAME.get(from_agent, from_agent)
        to_name = AGENT_ID_TO_NAME.get(to_agent, to_agent)

        prompt = f"""
[INTER-AGENT REQUEST]
From: {from_name} ({from_agent})
To: {to_name} ({to_agent})

{from_name} is asking for your input:
{question}

Please provide a clear, concise answer focusing on your area of expertise.
This will be used by {from_name} to provide a complete response to the user.
"""
        return prompt

    def should_consult_agent(self, text: str, current_agent: str) -> Optional[Dict[str, str]]:
        """
        Determine if current agent should consult another agent

        Args:
            text: User's question/request
            current_agent: Current agent processing request

        Returns:
            Dict with agent_id and reason, or None

        Example:
            Product Manager receives: "Can we build this feature?"
            Returns: {"agent_id": "engineer", "reason": "technical feasibility assessment"}
        """
        suggested_agent = self.detect_agent_needed(text, current_agent)

        if not suggested_agent:
            return None

        # Determine reason based on agent pairing
        reasons = {
            ("product_manager", "engineer"): "technical feasibility and implementation details",
            ("product_manager", "finance_manager"): "budget and cost analysis",
            ("product_manager", "marketing_strategist"): "market positioning and messaging",
            ("marketing_strategist", "finance_manager"): "campaign budget and ROI projections",
            ("marketing_strategist", "outbound_emailer"): "email campaign execution",
            ("finance_manager", "product_manager"): "product revenue impact analysis",
            ("engineer", "product_manager"): "product requirements and specifications",
        }

        reason = reasons.get((current_agent, suggested_agent), f"{AGENT_ID_TO_NAME[suggested_agent]}'s expertise")

        return {
            "agent_id": suggested_agent,
            "agent_name": AGENT_ID_TO_NAME[suggested_agent],
            "reason": reason
        }

    def extract_agent_response(self, full_response: str, agent_name: str) -> str:
        """
        Extract just the agent's answer from a formatted response

        Args:
            full_response: Full LLM response
            agent_name: Name of agent who responded

        Returns:
            Cleaned response text
        """
        # Remove any [INTER-AGENT REQUEST] headers
        response = re.sub(r'\[INTER-AGENT REQUEST\].*?(?=\n\n|\Z)', '', full_response, flags=re.DOTALL)

        # Remove "From:", "To:" lines
        response = re.sub(r'^(From|To):.*$', '', response, flags=re.MULTILINE)

        return response.strip()


# Global instance
agent_router = AgentRouter()
