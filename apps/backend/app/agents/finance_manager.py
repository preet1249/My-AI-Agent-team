"""
Finance Manager Agent - Analyzes finances, tracks expenses, provides budget insights
Uses NVIDIA NeMo 340B for financial analysis
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
import logging

logger = logging.getLogger(__name__)


class FinanceManagerAgent:
    """
    Finance Manager AI Agent
    - Analyzes financial data
    - Tracks expenses and revenue
    - Provides budget insights
    - Creates financial forecasts
    """

    def __init__(self):
        self.agent_name = "finance_manager"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process finance management request

        Args:
            user_id: User UUID
            prompt: User's finance request
            context: Optional context (expense data, revenue, etc.)
            external_id: Optional idempotency key

        Returns:
            Dict with financial analysis and recommendations
        """
        external_id = external_id or generate_external_id("finance")

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
            # Enhance context with financial data
            if not context:
                context = {}

            # Fetch recent campaigns for cost analysis
            recent_campaigns = supabase_client.table("campaigns") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(10) \
                .execute()

            if recent_campaigns.data:
                context["recent_campaigns"] = recent_campaigns.data

            # Call LLM
            response = await self.client.call_finance_manager(prompt, context)

            # Extract metrics
            metrics = self._extract_financial_metrics(response)

            # Update task as completed
            output = {
                "response": response,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Finance Manager task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Finance Manager task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    def _extract_financial_metrics(self, response: str) -> Dict[str, Any]:
        """
        Extract financial metrics from response

        Args:
            response: LLM response

        Returns:
            Dict with extracted metrics
        """
        # Simple metric extraction
        metrics = {
            "summary": response[:200] if len(response) > 200 else response,
            "recommendations": []
        }

        # Look for dollar amounts
        import re
        dollar_matches = re.findall(r'\$[\d,]+(?:\.\d{2})?', response)
        if dollar_matches:
            metrics["mentioned_amounts"] = dollar_matches

        return metrics


# Global instance
finance_manager_agent = FinanceManagerAgent()
