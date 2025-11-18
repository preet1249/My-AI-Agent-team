"""
Personal AI Assistant - Sophia
Has access to ALL app data and can coordinate with other agents
Most intelligent agent with full context awareness
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
from app.utils.agent_router import agent_router, AGENT_ID_TO_NAME
import logging
import json

logger = logging.getLogger(__name__)


class PersonalAssistantAgent:
    """
    Personal AI Assistant - Sophia (Female)

    Capabilities:
    - Access to ALL user data (tasks, leads, emails, calendar, insights, campaigns)
    - Can call other agents for specialized help
    - Intelligent task assignment
    - Context-aware responses
    - Auto-scheduling and organization
    """

    def __init__(self):
        self.agent_name = "personal_assistant"
        self.name = "Sophia"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process personal assistant request with full app context

        Args:
            user_id: User UUID
            prompt: User's request
            context: Optional additional context
            external_id: Optional idempotency key

        Returns:
            Dict with response and actions taken
        """
        external_id = external_id or generate_external_id("assistant")

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
            # Gather COMPLETE context from entire app
            full_context = await self._gather_full_context(user_id)

            # Check if need to consult other agents
            consultation = agent_router.should_consult_agent(prompt, self.agent_name)

            if consultation:
                # Get input from other agent
                logger.info(f"Sophia consulting {consultation['agent_name']} for {consultation['reason']}")
                agent_input = await self._consult_agent(
                    user_id,
                    consultation['agent_id'],
                    prompt
                )
                full_context["agent_consultation"] = {
                    "agent": consultation['agent_name'],
                    "input": agent_input
                }

            # Generate response with full context
            response = await self._generate_response(prompt, full_context)

            # Execute any actions (task assignment, scheduling, etc.)
            actions = await self._execute_actions(user_id, response, prompt)

            # Update task as completed
            output = {
                "response": response,
                "actions_taken": actions,
                "consulted_agents": [consultation] if consultation else [],
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Personal Assistant task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Personal Assistant task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    async def _gather_full_context(self, user_id: str) -> Dict[str, Any]:
        """
        Gather complete context from all app data

        Returns comprehensive user data including:
        - Recent tasks and their status
        - Leads and their engagement
        - Email history
        - Calendar events
        - Product insights
        - Marketing campaigns
        - Conversation history
        """
        context = {}

        # Recent tasks (last 20)
        tasks = supabase_client.table("agent_tasks") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()
        context["recent_tasks"] = tasks.data if tasks.data else []

        # Leads (top 30 by score)
        leads = supabase_client.table("leads") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("score", desc=True) \
            .limit(30) \
            .execute()
        context["leads"] = leads.data if leads.data else []

        # Calendar events (upcoming)
        upcoming_events = supabase_client.table("calendar_events") \
            .select("*") \
            .eq("user_id", user_id) \
            .gte("start_time", datetime.utcnow().isoformat()) \
            .order("start_time") \
            .limit(20) \
            .execute()
        context["calendar"] = upcoming_events.data if upcoming_events.data else []

        # Product insights (recent 10)
        insights = supabase_client.table("product_insights") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute()
        context["insights"] = insights.data if insights.data else []

        # Campaigns (recent 10)
        campaigns = supabase_client.table("campaigns") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(10) \
            .execute()
        context["campaigns"] = campaigns.data if campaigns.data else []

        # Email events (last 50)
        email_events = supabase_client.table("email_events") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        context["email_activity"] = email_events.data if email_events.data else []

        # Alerts (unread)
        alerts = supabase_client.table("alerts") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("read", False) \
            .order("created_at", desc=True) \
            .execute()
        context["alerts"] = alerts.data if alerts.data else []

        return context

    async def _consult_agent(
        self,
        user_id: str,
        agent_id: str,
        question: str
    ) -> str:
        """
        Consult another agent for their expertise

        Args:
            user_id: User ID
            agent_id: Agent to consult
            question: Question to ask

        Returns:
            Agent's response
        """
        # Import agents dynamically to avoid circular imports
        from app.agents.product_manager import product_manager_agent
        from app.agents.finance_manager import finance_manager_agent
        from app.agents.marketing_strategist import marketing_strategist_agent
        from app.agents.engineer import engineer_agent

        agents = {
            "product_manager": product_manager_agent,
            "finance_manager": finance_manager_agent,
            "marketing_strategist": marketing_strategist_agent,
            "engineer": engineer_agent
        }

        agent = agents.get(agent_id)
        if not agent:
            return f"Agent {agent_id} not available"

        # Format request
        formatted_question = agent_router.format_agent_request(
            from_agent=self.agent_name,
            to_agent=agent_id,
            question=question
        )

        # Get agent's response
        result = await agent.process(
            user_id=user_id,
            prompt=formatted_question,
            external_id=generate_external_id(f"sophia-consult-{agent_id}")
        )

        return result.get("response", "No response")

    async def _generate_response(
        self,
        prompt: str,
        full_context: Dict[str, Any]
    ) -> str:
        """
        Generate intelligent response with full context awareness

        Args:
            prompt: User's request
            full_context: Complete app context

        Returns:
            Sophia's response
        """
        # Build system prompt with Sophia's personality
        system_prompt = f"""
You are Sophia, the Personal AI Assistant.

You have access to ALL user data and can see:
- {len(full_context.get('recent_tasks', []))} recent tasks
- {len(full_context.get('leads', []))} leads
- {len(full_context.get('calendar', []))} upcoming calendar events
- {len(full_context.get('insights', []))} product insights
- {len(full_context.get('campaigns', []))} marketing campaigns
- {len(full_context.get('email_activity', []))} recent email activities

You are intelligent, proactive, and organized. You:
- Understand context from past conversations and data
- Assign tasks intelligently with specific dates/times
- Coordinate with other agents (Alex, Marcus, Ryan, Jake, Chris, Daniel, Kevin)
- Provide actionable, structured responses
- Anticipate user needs

Be conversational but professional. Think like an executive assistant who knows everything about the user's business.
"""

        # Format context for LLM (use TOON for token efficiency)
        from app.utils.toon_converter import toon_converter

        context_str = toon_converter.json_to_toon(full_context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"User Data:\n{context_str}"},
            {"role": "user", "content": prompt}
        ]

        # Call NVIDIA NeMo (most powerful model for Sophia)
        response = await self.client.call_model(
            model="nvidia/nemotron-4-340b-instruct",
            messages=messages,
            temperature=0.7,
            max_tokens=3000
        )

        return response["content"]

    async def _execute_actions(
        self,
        user_id: str,
        response: str,
        original_prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Execute actions based on Sophia's response
        (e.g., create calendar events, assign tasks, create alerts)

        Args:
            user_id: User ID
            response: Sophia's response
            original_prompt: Original user prompt

        Returns:
            List of actions taken
        """
        actions = []

        # Detect if scheduling/task assignment mentioned
        if any(keyword in original_prompt.lower() for keyword in ["assign", "schedule", "task", "calendar"]):
            # Extract and create calendar events (simple implementation)
            # In production, use more sophisticated NLP/parsing

            # For now, just log the action
            actions.append({
                "type": "task_assignment_suggested",
                "details": "Task assignment logic to be implemented based on Sophia's response"
            })

        return actions


# Global instance
personal_assistant_agent = PersonalAssistantAgent()
