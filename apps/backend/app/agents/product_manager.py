"""
Product Manager Agent - Analyzes trends, creates insights, manages roadmaps
Uses NVIDIA NeMo 340B for strategic analysis
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


class ProductManagerAgent:
    """
    Product Manager AI Agent
    - Analyzes market trends
    - Creates product insights
    - Manages product roadmaps
    - Provides strategic recommendations
    """

    def __init__(self):
        self.agent_name = "product_manager"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process product management request

        Args:
            user_id: User UUID
            prompt: User's product management request
            context: Optional context (trends data, competitor info, etc.)
            external_id: Optional idempotency key

        Returns:
            Dict with analysis, insights, and recommendations
        """
        external_id = external_id or generate_external_id("pm")

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
            # Get conversation ID from context or generate new one
            conversation_id = context.get("conversation_id", f"conv_{user_id}_{task_id}") if context else f"conv_{user_id}_{task_id}"

            # Get conversation history for context
            conversation_history = await conversation_memory.get_conversation_context(conversation_id)

            # Add user message to conversation history
            await conversation_memory.add_message(
                conversation_id=conversation_id,
                role="user",
                content=prompt,
                metadata={"task_id": task_id}
            )

            # Enhance context with existing insights
            if not context:
                context = {}

            # Fetch recent product insights
            recent_insights = supabase_client.table("product_insights") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(5) \
                .execute()

            if recent_insights.data:
                context["recent_insights"] = recent_insights.data

            # Get magic system prompt with business context
            business_context = context.get("business_context")
            system_prompt = system_prompt_manager.get_agent_prompt(
                agent_name=self.agent_name,
                business_context=business_context
            )

            # Build messages with conversation history
            messages = [{"role": "system", "content": system_prompt}]

            # Add conversation history
            messages.extend(conversation_history)

            # Add current user prompt
            messages.append({"role": "user", "content": prompt})

            # Add context as TOON if provided
            if context.get("recent_insights"):
                context_str = toon_converter.json_to_toon({"insights": context["recent_insights"]})
                messages.append({
                    "role": "system",
                    "content": f"Recent Product Insights:\n{context_str}"
                })

            # Call LLM with full context
            response = await self.client.call_model(
                model="nvidia/nemotron-nano-12b-v2-vl:free",
                messages=messages,
                temperature=0.7,
                max_tokens=2500
            )

            response_content = response["content"]

            # Save assistant response to conversation history
            await conversation_memory.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_content,
                agent_name=self.agent_name,
                metadata={"task_id": task_id, "tokens_used": response.get("tokens_used")}
            )

            # Parse response and extract insights
            insights = self._extract_insights(response_content)

            # Store insights in database
            if insights:
                for insight in insights:
                    insight_record = {
                        "user_id": user_id,
                        "title": insight.get("title", "Product Insight"),
                        "content": insight.get("content", response_content),
                        "tags": insight.get("tags", []),
                        "priority": insight.get("priority", "medium"),
                        "source": "product_manager_agent",
                        "metadata": {"task_id": task_id}
                    }
                    supabase_client.table("product_insights").insert(insight_record).execute()

            # Update task as completed
            output = {
                "response": response_content,
                "insights": insights,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Product Manager task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Product Manager task {task_id} failed: {e}")

            # Update task as failed
            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    def _extract_insights(self, response: str) -> list:
        """
        Extract structured insights from LLM response

        Args:
            response: LLM response text

        Returns:
            List of insight dicts
        """
        # Simple extraction - look for bullet points or numbered lists
        insights = []
        lines = response.split("\n")

        current_insight = None
        for line in lines:
            line = line.strip()

            # Check for insight headers
            if any(keyword in line.lower() for keyword in ["insight:", "recommendation:", "key finding:"]):
                if current_insight:
                    insights.append(current_insight)

                current_insight = {
                    "title": line.replace(":", "").strip(),
                    "content": "",
                    "tags": [],
                    "priority": "medium"
                }

            elif current_insight and line:
                current_insight["content"] += line + " "

        if current_insight:
            insights.append(current_insight)

        return insights


# Global instance
product_manager_agent = ProductManagerAgent()
