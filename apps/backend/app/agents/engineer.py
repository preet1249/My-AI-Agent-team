"""
Engineer Agent - Writes code, debugs, and provides technical solutions
Uses Claude 3 Haiku for code generation
"""
from typing import Dict, Any, Optional
from datetime import datetime
from app.utils.openrouter_client import openrouter_client
from app.database import supabase_client
from app.utils.security import generate_external_id
import logging

logger = logging.getLogger(__name__)


class EngineerAgent:
    """
    Engineer AI Agent
    - Writes code snippets and scripts
    - Debugs technical issues
    - Provides architecture recommendations
    - Generates documentation
    """

    def __init__(self):
        self.agent_name = "engineer"
        self.client = openrouter_client

    async def process(
        self,
        user_id: str,
        prompt: str,
        language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        external_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process engineering request

        Args:
            user_id: User UUID
            prompt: User's technical request
            language: Programming language (python, javascript, etc.)
            context: Optional technical context
            external_id: Optional idempotency key

        Returns:
            Dict with code, explanation, and documentation
        """
        external_id = external_id or generate_external_id("engineer")

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
                "prompt": prompt,
                "language": language,
                "context": context
            },
            "status": "processing",
            "external_id": external_id,
            "created_at": datetime.utcnow().isoformat()
        }

        task_result = supabase_client.table("agent_tasks").insert(task).execute()
        task_id = task_result.data[0]["id"]

        try:
            # Enhance prompt with language context
            enhanced_prompt = prompt
            if language:
                enhanced_prompt = f"Using {language}, {prompt}"

            # Call LLM
            response = await self.client.call_engineer(enhanced_prompt, context)

            # Extract code blocks if present
            code_blocks = self._extract_code_blocks(response)

            # Update task as completed
            output = {
                "response": response,
                "code_blocks": code_blocks,
                "language": language,
                "timestamp": datetime.utcnow().isoformat()
            }

            supabase_client.table("agent_tasks") \
                .update({"status": "completed", "output": output}) \
                .eq("id", task_id) \
                .execute()

            logger.info(f"Engineer task {task_id} completed successfully")
            return output

        except Exception as e:
            logger.error(f"Engineer task {task_id} failed: {e}")

            supabase_client.table("agent_tasks") \
                .update({
                    "status": "failed",
                    "error": str(e)
                }) \
                .eq("id", task_id) \
                .execute()

            raise

    def _extract_code_blocks(self, response: str) -> list:
        """
        Extract code blocks from markdown response

        Args:
            response: LLM response with code blocks

        Returns:
            List of code block dicts
        """
        import re

        # Pattern for markdown code blocks
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)

        code_blocks = []
        for lang, code in matches:
            code_blocks.append({
                "language": lang or "text",
                "code": code.strip()
            })

        return code_blocks


# Global instance
engineer_agent = EngineerAgent()
