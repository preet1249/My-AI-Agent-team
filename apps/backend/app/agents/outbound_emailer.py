"""
Outbound Emailer Agent - Sends personalized emails via Gmail API
Uses NVIDIA NeMo for email generation with conversation memory
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
from app.utils.system_prompts import system_prompt_manager
from app.utils.conversation_memory import conversation_memory
from app.redis_client import redis_queue
import logging

logger = logging.getLogger(__name__)


class OutboundEmailerAgent:
    """
    Outbound Emailer AI Agent
    - Generates personalized email content
    - Sends emails via Gmail API
    - Tracks email events (sent, opened, clicked, replied)
    - Follows up based on engagement
    """

    def __init__(self):
        self.agent_name = "outbound_emailer"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        lead_ids: List[str],
        campaign_id: Optional[str] = None,
        template: Optional[str] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process outbound email campaign

        Args:
            user_id: User UUID
            lead_ids: List of lead UUIDs to email
            campaign_id: Optional campaign UUID
            template: Optional email template
            external_id: Optional idempotency key

        Returns:
            Dict with email send results
        """
        external_id = external_id or generate_external_id("email")

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
                "lead_ids": lead_ids,
                "campaign_id": campaign_id,
                "template": template
            },
            "status": "processing",
            "external_id": external_id,
            "created_at": datetime.utcnow().isoformat()
        }

        task_result = supabase_client.table("agent_tasks").insert(task).execute()
        task_id = task_result.data[0]["id"]

        try:
            emails_sent = []

            for lead_id in lead_ids:
                # Fetch lead data
                lead_result = supabase_client.table("leads") \
                    .select("*") \
                    .eq("id", lead_id) \
                    .single() \
                    .execute()

                lead = lead_result.data
                if not lead or not lead.get("email"):
                    logger.warning(f"Lead {lead_id} has no email address")
                    continue

                # Generate personalized email
                email_content = await self._generate_email(lead, template)

                # Enqueue email send job (worker handles actual sending via Gmail)
                email_job = {
                    "lead_id": lead_id,
                    "to_email": lead["email"],
                    "subject": email_content["subject"],
                    "body": email_content["body"],
                    "campaign_id": campaign_id,
                    "task_id": task_id,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }

                await redis_queue.enqueue("email_queue", email_job)

                # Track email event
                event_record = {
                    "user_id": user_id,
                    "lead_id": lead_id,
                    "event_type": "queued",
                    "metadata": {
                        "campaign_id": campaign_id,
                        "task_id": task_id
                    }
                }
                supabase_client.table("email_events").insert(event_record).execute()

                emails_sent.append({
                    "lead_id": lead_id,
                    "email": lead["email"],
                    "status": "queued"
                })

                logger.info(f"Queued email for lead {lead_id}")

            # Update task as completed
            output = {
                "emails_sent": len(emails_sent),
                "details": emails_sent,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Outbound Emailer task {task_id} completed. Queued {len(emails_sent)} emails")
            return output

        except Exception as e:
            logger.error(f"Outbound Emailer task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    async def _generate_email(
        self,
        lead: Dict[str, Any],
        template: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate personalized email content using magic system prompt

        Args:
            lead: Lead data
            template: Optional template

        Returns:
            Dict with subject and body
        """
        # Get magic system prompt
        business_context = {
            "lead_company": lead.get('company', 'N/A'),
            "lead_metadata": lead.get('metadata', {}),
            "template": template
        }

        system_prompt = system_prompt_manager.get_agent_prompt(
            agent_name=self.agent_name,
            business_context=business_context
        )

        prompt = f"""
        Generate a personalized outbound email for this lead:

        Company: {lead.get('company', 'N/A')}
        Name: {lead.get('name', '')}
        Email: {lead.get('email')}
        Role: {lead.get('metadata', {}).get('role', 'Unknown')}
        Company Description: {lead.get('metadata', {}).get('company_description', '')}

        Template: {template or 'Professional B2B outreach email'}

        Generate:
        1. Subject line (max 60 chars, personalized)
        2. Email body (personalized, professional, brief, value-focused)

        Return JSON: {{"subject": "...", "body": "..."}}
        """

        try:
            response = await self.client.call_model(
                model="nvidia/nemotron-nano-12b-v2-vl:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                extra_body={
                    "reasoning": {"enabled": True}
                }
            )

            import json
            email_data = json.loads(response["content"])
            return email_data

        except Exception as e:
            logger.error(f"Failed to generate email: {e}")
            # Fallback with personalized data
            company_name = lead.get('company', 'your business')
            person_name = lead.get('name', 'there')

            return {
                "subject": f"Quick question about {company_name}",
                "body": f"Hi {person_name},\n\nI noticed {company_name} and wanted to reach out.\n\nBest regards"
            }


# Global instance
outbound_emailer_agent = OutboundEmailerAgent()
