"""
Booking & Call Prep Agent - Schedules meetings and generates call scripts
Uses Claude Haiku for script generation
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
import logging

logger = logging.getLogger(__name__)


class BookingCallPrepAgent:
    """
    Booking & Call Prep AI Agent
    - Generates call scripts and prep materials
    - Schedules calendar events
    - Creates meeting agendas
    - Provides talking points
    """

    def __init__(self):
        self.agent_name = "booking_callprep"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        lead_id: Optional[str] = None,
        meeting_type: str = "discovery",
        scheduled_time: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process call prep request

        Args:
            user_id: User UUID
            lead_id: Optional lead UUID
            meeting_type: Type of meeting (discovery, demo, closing, etc.)
            scheduled_time: ISO timestamp for meeting
            external_id: Optional idempotency key

        Returns:
            Dict with call script and calendar event
        """
        external_id = external_id or generate_external_id("callprep")

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
            "input": {
                "lead_id": lead_id,
                "meeting_type": meeting_type,
                "scheduled_time": scheduled_time
            },
            "status": "processing",
            "external_id": external_id,
            "created_at": datetime.utcnow().isoformat()
        }

        task_result = supabase_client.table("agent_tasks").insert(task).execute()
        task_id = task_result.data[0]["id"]

        try:
            context = {}

            # Fetch lead data if provided
            if lead_id:
                lead_result = supabase_client.table("leads") \
                    .select("*") \
                    .eq("id", lead_id) \
                    .single() \
                    .execute()

                if lead_result.data:
                    context["lead"] = lead_result.data

                    # Fetch email history with this lead
                    email_history = supabase_client.table("email_events") \
                        .select("*") \
                        .eq("lead_id", lead_id) \
                        .order("created_at", desc=True) \
                        .limit(5) \
                        .execute()

                    if email_history.data:
                        context["email_history"] = email_history.data

            # Generate call script
            script = await self._generate_call_script(meeting_type, context)

            # Store call script
            script_record = {
                "user_id": user_id,
                "lead_id": lead_id,
                "meeting_type": meeting_type,
                "script": script,
                "metadata": {"task_id": task_id}
            }
            script_result = supabase_client.table("call_scripts").insert(script_record).execute()
            script_id = script_result.data[0]["id"]

            # Create calendar event if time provided
            calendar_event = None
            if scheduled_time:
                event_record = {
                    "user_id": user_id,
                    "title": f"{meeting_type.title()} Call - {context.get('lead', {}).get('company', 'Lead')}",
                    "start_time": scheduled_time,
                    "duration_minutes": 30,  # default
                    "metadata": {
                        "lead_id": lead_id,
                        "script_id": script_id,
                        "task_id": task_id
                    }
                }
                calendar_result = supabase_client.table("calendar_events").insert(event_record).execute()
                calendar_event = calendar_result.data[0]

            # Update task as completed
            output = {
                "script": script,
                "script_id": script_id,
                "calendar_event": calendar_event,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Booking Call Prep task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Booking Call Prep task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    async def _generate_call_script(
        self,
        meeting_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate call script using LLM

        Args:
            meeting_type: Type of meeting
            context: Lead and email history

        Returns:
            Call script dict
        """
        lead = context.get("lead", {})
        email_history = context.get("email_history", [])

        prompt = f"""
        Generate a call script for a {meeting_type} call.

        Lead Information:
        - Company: {lead.get('company', 'N/A')}
        - Email: {lead.get('email', 'N/A')}
        - Score: {lead.get('score', 0)}/100
        - Metadata: {lead.get('metadata', {})}

        Previous Interactions: {len(email_history)} emails exchanged

        Generate a structured call script with:
        1. Opening (introduction, rapport building)
        2. Discovery questions (3-5 questions)
        3. Value proposition
        4. Objection handling
        5. Next steps / closing

        Return JSON format.
        """

        try:
            response = await self.client.call_model(
                model="anthropic/claude-3-haiku",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=1500
            )

            import json
            script = json.loads(response["content"])
            return script

        except Exception as e:
            logger.error(f"Failed to generate call script: {e}")
            # Fallback script
            return {
                "opening": f"Hi, thanks for taking the time to speak with me about {lead.get('company', 'your business')}.",
                "discovery_questions": [
                    "What are your current challenges?",
                    "What solutions have you tried?",
                    "What's your timeline?"
                ],
                "value_proposition": "We help companies like yours achieve their goals.",
                "next_steps": "Would you like to schedule a follow-up?"
            }


# Global instance
booking_callprep_agent = BookingCallPrepAgent()
