"""
Marketing Strategist Agent - Creates campaigns, analyzes performance, optimizes strategies
Uses NVIDIA NeMo 340B for creative marketing
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
import logging

logger = logging.getLogger(__name__)


class MarketingStrategistAgent:
    """
    Marketing Strategist AI Agent
    - Creates marketing campaigns
    - Analyzes campaign performance
    - Optimizes marketing strategies
    - Generates creative content ideas
    """

    def __init__(self):
        self.agent_name = "marketing_strategist"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process marketing strategy request

        Args:
            user_id: User UUID
            prompt: User's marketing request
            context: Optional context (campaign data, audience info, etc.)
            external_id: Optional idempotency key

        Returns:
            Dict with campaign ideas and strategies
        """
        external_id = external_id or generate_external_id("marketing")

        # Check for duplicate request
        existing = supabase_client.table("agent_tasks") \
            .select("*") \
            .eq("external_id", external_id) \
            .execute()

        if existing.data:
            logger.info(f"Returning cached result for external_id: {external_id}")
            return existing.data[0]["output"]

        # Create task record
        task = {
            "user_id": user_id,
            "agent_name": self.agent_name,
            "input": {"prompt": prompt, "context": context},
            "status": "processing",
            "external_id": external_id,
            "created_at": datetime.utcnow().isoformat()
        }

        task_result = supabase_client.table("agent_tasks").insert(task).execute()
        task_id = task_result.data[0]["id"]

        try:
            # Enhance context with campaign data
            if not context:
                context = {}

            # Fetch existing campaigns
            existing_campaigns = supabase_client.table("campaigns") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(5) \
                .execute()

            if existing_campaigns.data:
                context["existing_campaigns"] = existing_campaigns.data

            # Fetch lead data for targeting insights
            lead_stats = supabase_client.table("leads") \
                .select("company, metadata") \
                .eq("user_id", user_id) \
                .limit(20) \
                .execute()

            if lead_stats.data:
                context["lead_insights"] = lead_stats.data

            # Call LLM
            response = await self.client.call_marketing_strategist(prompt, context)

            # Extract campaign ideas
            campaigns = self._extract_campaigns(response)

            # Store campaigns if structured
            if campaigns:
                for campaign in campaigns:
                    campaign_record = {
                        "user_id": user_id,
                        "name": campaign.get("name", "Marketing Campaign"),
                        "channel": campaign.get("channel", "email"),
                        "status": "draft",
                        "metadata": {
                            "description": campaign.get("description", ""),
                            "task_id": task_id
                        }
                    }
                    supabase_client.table("campaigns").insert(campaign_record).execute()

            # Update task as completed
            output = {
                "response": response,
                "campaigns": campaigns,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Marketing Strategist task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Marketing Strategist task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    def _extract_campaigns(self, response: str) -> list:
        """
        Extract campaign ideas from response

        Args:
            response: LLM response

        Returns:
            List of campaign dicts
        """
        campaigns = []
        lines = response.split("\n")

        current_campaign = None
        for line in lines:
            line = line.strip()

            # Look for campaign headers
            if any(keyword in line.lower() for keyword in ["campaign:", "strategy:", "idea:"]):
                if current_campaign:
                    campaigns.append(current_campaign)

                current_campaign = {
                    "name": line.replace(":", "").strip(),
                    "description": "",
                    "channel": "email"  # default
                }

            elif current_campaign and line:
                current_campaign["description"] += line + " "

        if current_campaign:
            campaigns.append(current_campaign)

        return campaigns


# Global instance
marketing_strategist_agent = MarketingStrategistAgent()
