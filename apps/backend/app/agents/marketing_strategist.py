"""
Marketing Strategist Agent - Creates campaigns, analyzes performance, optimizes strategies
Uses NVIDIA NeMo 340B for creative marketing with conversation memory
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
from app.utils.system_prompts import system_prompt_manager
from app.utils.conversation_memory import conversation_memory
from app.utils.toon_converter import toon_converter
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
            # Get or create conversation ID
            conversation_id = context.get("conversation_id") if context else None
            if not conversation_id:
                conversation_id = f"marketing_{user_id}_{task_id}"

            # Get conversation history
            conversation_history = await conversation_memory.get_conversation_context(conversation_id)

            # Add user message to history
            await conversation_memory.add_message(
                conversation_id=conversation_id,
                role="user",
                content=prompt,
                agent_name=self.agent_name,
                metadata={"task_id": task_id}
            )

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

            # Build business context for magic prompt
            business_context = {
                "existing_campaigns": existing_campaigns.data if existing_campaigns.data else [],
                "lead_insights": lead_stats.data if lead_stats.data else [],
                "marketing_context": context.get("marketing_data", {})
            }

            # Get magic system prompt
            system_prompt = system_prompt_manager.get_agent_prompt(
                agent_name=self.agent_name,
                business_context=business_context
            )

            # Convert context to TOON format if large
            context_str = f"Marketing Context:\n{context}" if context else ""
            if len(context_str) > 500:
                context_str = toon_converter.to_toon(context)

            # Build messages with conversation history
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            messages.extend(conversation_history)

            # Add current user message with context
            current_message = prompt
            if context_str:
                current_message = f"{prompt}\n\n{context_str}"
            messages.append({"role": "user", "content": current_message})

            # Call LLM with NVIDIA NeMo reasoning
            response = await self.client.call_model(
                model="nvidia/nemotron-nano-12b-v2-vl:free",
                messages=messages,
                temperature=0.8,  # Higher temp for creative marketing
                max_tokens=2500,
                extra_body={
                    "reasoning": {"enabled": True}
                }
            )

            # Extract response content
            response_content = response.get("content", "")

            # Save assistant response to conversation memory
            await conversation_memory.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_content,
                agent_name=self.agent_name,
                metadata={"task_id": task_id}
            )

            # Extract campaign ideas
            campaigns = self._extract_campaigns(response_content)

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
                "response": response_content,
                "campaigns": campaigns,
                "conversation_id": conversation_id,
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
