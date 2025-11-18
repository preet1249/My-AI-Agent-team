"""
OpenRouter API Client for LLM calls
Supports NVIDIA NeMo, Claude, and other models with retry logic
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.utils.toon_converter import toon_converter
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenRouterClient:
    """
    OpenRouter API client with retry logic and rate limiting
    """

    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.timeout = settings.MODEL_CALL_TIMEOUT

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError))
    )
    async def call_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_toon: bool = False,
        extra_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Call OpenRouter model with retry logic

        Args:
            model: Model identifier (e.g., "nvidia/nemotron-4-340b-instruct")
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            use_toon: Convert messages to TOON format for token efficiency
            extra_params: Additional model-specific parameters

        Returns:
            Response dict with 'content', 'model', 'tokens_used'

        Raises:
            httpx.HTTPStatusError: If API returns error
            httpx.TimeoutException: If request times out
        """
        # Convert to TOON if requested and beneficial
        if use_toon and len(messages) > 2:
            messages = self._convert_to_toon_messages(messages)

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # Enable reasoning for NVIDIA NeMo models
        if "nvidia" in model.lower() or "nemotron" in model.lower():
            payload["extra_body"] = {"reasoning": {"enabled": True}}

        if extra_params:
            payload.update(extra_params)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-agent-team.app",
            "X-Title": "AI Agent Team"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                logger.info(f"Calling OpenRouter model: {model}")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

                # Extract content
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                logger.info(f"Model call successful. Tokens used: {tokens_used}")

                return {
                    "content": content,
                    "model": model,
                    "tokens_used": tokens_used,
                    "raw_response": data
                }

            except httpx.HTTPStatusError as e:
                logger.error(f"OpenRouter API error: {e.response.status_code} - {e.response.text}")
                raise

            except httpx.TimeoutException:
                logger.error(f"OpenRouter timeout after {self.timeout}s")
                raise

            except Exception as e:
                logger.error(f"Unexpected error calling OpenRouter: {e}")
                raise

    async def call_product_manager(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Product Manager agent (NVIDIA NeMo)

        Args:
            prompt: User prompt
            context: Optional context data

        Returns:
            Model response content
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Product Manager AI agent. "
                    "Analyze trends, create product insights, and manage roadmaps. "
                    "Provide actionable recommendations based on market data."
                )
            },
            {"role": "user", "content": prompt}
        ]

        if context:
            context_str = toon_converter.json_to_toon(context)
            messages.insert(1, {
                "role": "system",
                "content": f"Context:\n{context_str}"
            })

        response = await self.call_model(
            model=settings.PRODUCT_MANAGER_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        return response["content"]

    async def call_finance_manager(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Finance Manager agent (NVIDIA NeMo)

        Args:
            prompt: User prompt
            context: Optional financial data

        Returns:
            Model response content
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Finance Manager AI agent. "
                    "Analyze financial data, track expenses, and provide budget insights. "
                    "Give clear financial recommendations and forecasts."
                )
            },
            {"role": "user", "content": prompt}
        ]

        if context:
            context_str = toon_converter.json_to_toon(context)
            messages.insert(1, {
                "role": "system",
                "content": f"Financial Data:\n{context_str}"
            })

        response = await self.call_model(
            model=settings.FINANCE_MANAGER_MODEL,
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )

        return response["content"]

    async def call_marketing_strategist(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Marketing Strategist agent (NVIDIA NeMo)

        Args:
            prompt: User prompt
            context: Optional campaign data

        Returns:
            Model response content
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a Marketing Strategist AI agent. "
                    "Create marketing campaigns, analyze performance, and optimize strategies. "
                    "Provide creative and data-driven marketing recommendations."
                )
            },
            {"role": "user", "content": prompt}
        ]

        if context:
            context_str = toon_converter.json_to_toon(context)
            messages.insert(1, {
                "role": "system",
                "content": f"Campaign Data:\n{context_str}"
            })

        response = await self.call_model(
            model=settings.MARKETING_STRATEGIST_MODEL,
            messages=messages,
            temperature=0.8,
            max_tokens=2000
        )

        return response["content"]

    async def call_engineer(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call Engineer agent (Claude 3 Haiku)

        Args:
            prompt: User prompt
            context: Optional technical context

        Returns:
            Model response content
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an Engineer AI agent. "
                    "Write code, debug issues, and provide technical solutions. "
                    "Give clear, well-documented code examples."
                )
            },
            {"role": "user", "content": prompt}
        ]

        if context:
            context_str = toon_converter.json_to_toon(context)
            messages.insert(1, {
                "role": "system",
                "content": f"Technical Context:\n{context_str}"
            })

        response = await self.call_model(
            model=settings.ENGINEER_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=3000
        )

        return response["content"]

    def _convert_to_toon_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Convert large message contexts to TOON format

        Args:
            messages: Original messages

        Returns:
            Messages with TOON-formatted content where beneficial
        """
        converted = []
        for msg in messages:
            content = msg["content"]

            # Try parsing as JSON and converting to TOON
            try:
                import json
                data = json.loads(content)
                if toon_converter.should_use_toon(data):
                    toon_content = toon_converter.json_to_toon(data)
                    savings = toon_converter.get_token_savings(data)
                    logger.info(f"TOON conversion saved {savings['savings_percent']}% tokens")
                    converted.append({
                        "role": msg["role"],
                        "content": toon_content
                    })
                else:
                    converted.append(msg)
            except (json.JSONDecodeError, ValueError):
                # Not JSON, keep original
                converted.append(msg)

        return converted


# Global instance
openrouter_client = OpenRouterClient()
