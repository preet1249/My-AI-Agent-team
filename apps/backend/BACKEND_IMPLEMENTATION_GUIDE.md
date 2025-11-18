# AI Agent Team Backend - Complete Implementation Guide

## 🎯 Architecture Overview

This backend implements a production-grade AI Agent Team system with:
- **7 Specialized AI Agents**
- **FastAPI Orchestrator** with async workers
- **Redis Task Queue** for reliable job processing
- **Supabase Database** with 11 tables
- **4 Secure Webhooks** with HMAC verification
- **TOON Format** for token-efficient LLM communication
- **Rate Limiting, Caching, Retry Logic**
- **Prometheus Monitoring**

---

## 📁 Project Structure

```
apps/backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── database.py                # Supabase client setup
│   ├── redis_client.py            # Redis/Upstash connection
│   │
│   ├── agents/                    # AI Agent Handlers (7 agents)
│   │   ├── __init__.py
│   │   ├── product_manager.py     # Product Manager agent
│   │   ├── finance_manager.py     # Finance Manager agent
│   │   ├── marketing_strategist.py
│   │   ├── leadgen_scraper.py
│   │   ├── outbound_emailer.py
│   │   ├── booking_callprep.py
│   │   └── engineer.py            # Engineer agent (Claude)
│   │
│   ├── routes/                    # API Endpoints
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Main orchestration routes
│   │   ├── agents.py              # Agent management routes
│   │   ├── leads.py               # Leads CRUD
│   │   ├── calendar.py            # Calendar management
│   │   ├── campaigns.py           # Email campaigns
│   │   └── health.py              # Health checks
│   │
│   ├── webhooks/                  # Webhook Handlers
│   │   ├── __init__.py
│   │   ├── gmail.py               # Gmail push notifications
│   │   ├── scraper.py             # Scraper completion hooks
│   │   ├── calendar_booking.py   # External booking forms
│   │   └── monitoring.py          # Prometheus alerts
│   │
│   ├── workers/                   # Background Workers
│   │   ├── __init__.py
│   │   ├── task_worker.py         # Main task processor
│   │   ├── email_worker.py        # Email send/receive worker
│   │   ├── scraper_worker.py      # Web scraping worker
│   │   └── monitoring_worker.py   # Alert processing
│   │
│   ├── utils/                     # Utilities
│   │   ├── __init__.py
│   │   ├── toon_converter.py      # JSON ↔ TOON conversion
│   │   ├── security.py            # HMAC, JWT verification
│   │   ├── rate_limiter.py        # Rate limiting utilities
│   │   ├── cache.py               # Caching layer
│   │   ├── retry.py               # Retry with backoff
│   │   ├── openrouter_client.py   # OpenRouter API client
│   │   ├── gmail_client.py        # Gmail API client
│   │   └── metrics.py             # Prometheus metrics
│   │
│   └── middleware/                # Middleware
│       ├── __init__.py
│       ├── auth.py                # Supabase auth middleware
│       ├── error_handler.py       # Global error handling
│       └── logging.py             # Request logging
│
├── scrapers/                      # Puppeteer/Playwright scrapers
│   ├── Dockerfile                 # Scraper container
│   ├── package.json
│   └── src/
│       ├── index.js               # Main scraper entry
│       ├── politeness.js          # Rate limiting & caching
│       └── extractors.js          # Content extraction
│
├── tests/                         # Comprehensive tests
│   ├── test_agents.py
│   ├── test_webhooks.py
│   ├── test_workers.py
│   └── test_toon_converter.py
│
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Local development
├── Dockerfile                     # Production container
├── supabase_schema.sql            # Database schema
└── README.md                      # Project documentation
```

---

## 🔧 Key Implementation Files

### 1. Configuration (`app/config.py`)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Server
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str  # service_role key for backend

    # Redis/Upstash
    REDIS_URL: str

    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Gmail
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GMAIL_REFRESH_TOKEN: str

    # Security
    INTERNAL_SIGNING_KEY: str  # For JWT
    WEBHOOK_SECRET: str        # For HMAC

    # Agent Configuration
    PRODUCT_MANAGER_MODEL: str = "nvidia/nemotron-70b-instruct"
    ENGINEER_MODEL: str = "anthropic/claude-3-haiku"

    # Rate Limits
    MAX_CONCURRENT_MODEL_CALLS: int = 3
    MAX_CONCURRENT_SCRAPES: int = 4
    GMAIL_MAX_RPM: int = 250

    # Timeouts (seconds)
    MODEL_CALL_TIMEOUT: int = 20
    ENGINEER_TIMEOUT: int = 60
    SCRAPE_TIMEOUT: int = 15
    WEBHOOK_ACK_TIMEOUT: int = 1

    # Cache TTL (seconds)
    SCRAPE_CACHE_TTL: int = 86400  # 24 hours
    MODEL_CACHE_TTL: int = 86400

    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAYS: list = [2, 8, 20]  # Exponential backoff

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2. TOON Converter (`app/utils/toon_converter.py`)

```python
"""
TOON Format Converter - Token-efficient serialization
Converts JSON ↔ TOON for LLM communication
"""
import json
from typing import Any, Dict, List
import yaml

class TOONConverter:
    """
    TOON (Token-Optimized Object Notation) converter
    Reduces token usage by ~30-50% for structured data
    """

    @staticmethod
    def json_to_toon(data: Dict[str, Any], compact: bool = True) -> str:
        """
        Convert JSON to TOON format

        Args:
            data: Python dict/JSON object
            compact: Use compact formatting

        Returns:
            TOON formatted string (YAML-like)
        """
        # TOON is essentially YAML with stricter formatting
        toon_str = yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
            indent=2
        )

        if compact:
            # Remove unnecessary whitespace
            lines = toon_str.split('\n')
            toon_str = '\n'.join(line.rstrip() for line in lines if line.strip())

        return toon_str

    @staticmethod
    def toon_to_json(toon_str: str) -> Dict[str, Any]:
        """
        Convert TOON to JSON/dict

        Args:
            toon_str: TOON formatted string

        Returns:
            Python dictionary
        """
        try:
            return yaml.safe_load(toon_str)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid TOON format: {e}")

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4

    @staticmethod
    def should_use_toon(data: Dict[str, Any], threshold: int = 1000) -> bool:
        """
        Determine if TOON conversion is beneficial

        Args:
            data: Data to check
            threshold: Token threshold (default 1000)

        Returns:
            True if data is large enough to benefit from TOON
        """
        json_str = json.dumps(data)
        tokens = len(json_str) // 4
        return tokens > threshold

# Global instance
toon_converter = TOONConverter()
```

### 3. Security Utilities (`app/utils/security.py`)

```python
"""
Security utilities for webhooks and internal auth
"""
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Header
from app.config import get_settings

settings = get_settings()

def verify_webhook_signature(
    payload: bytes,
    signature_header: str,
    secret: str = settings.WEBHOOK_SECRET
) -> bool:
    """
    Verify HMAC SHA256 webhook signature

    Args:
        payload: Raw request body bytes
        signature_header: x-webhook-signature header value
        secret: Webhook secret

    Returns:
        True if signature is valid
    """
    if not signature_header:
        return False

    # Extract signature (format: "sha256=<hex>")
    if not signature_header.startswith('sha256='):
        return False

    received_sig = signature_header.replace('sha256=', '')

    # Compute expected signature
    expected_sig = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(received_sig, expected_sig)

def create_internal_jwt(
    issuer: str = "orchestrator",
    audience: str = "worker",
    expires_in_seconds: int = 60
) -> str:
    """
    Create internal JWT for agent-to-agent calls

    Args:
        issuer: Token issuer
        audience: Token audience
        expires_in_seconds: Expiration time

    Returns:
        JWT token string
    """
    payload = {
        "iss": issuer,
        "aud": audience,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in_seconds),
        "iat": datetime.utcnow()
    }

    token = jwt.encode(
        payload,
        settings.INTERNAL_SIGNING_KEY,
        algorithm="HS256"
    )

    return token

def verify_internal_jwt(
    token: str,
    expected_audience: str = "worker"
) -> dict:
    """
    Verify internal JWT token

    Args:
        token: JWT token string
        expected_audience: Expected audience claim

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.INTERNAL_SIGNING_KEY,
            algorithms=["HS256"],
            audience=expected_audience
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_internal_auth(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    FastAPI dependency for verifying internal auth

    Usage:
        @router.post("/internal/endpoint")
        async def endpoint(auth: dict = Depends(verify_internal_auth)):
            ...
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization.replace("Bearer ", "")
    return verify_internal_jwt(token)
```

---

## 🚀 Agent Implementation Pattern

Each agent follows this pattern (`app/agents/product_manager.py`):

```python
"""
Product Manager Agent - NVIDIA NeMo 12B-2VL
Analyzes trends, creates product insights, manages roadmaps
"""
from typing import Dict, Any, List
import logging
from app.utils.toon_converter import toon_converter
from app.utils.openrouter_client import openrouter_client
from app.utils.cache import cache_manager
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class ProductManagerAgent:
    """Product Manager AI Agent"""

    SYSTEM_PROMPT = """You are ProductManagerAgent.
Output must be in TOON format with fields:
- title
- summary
- insights[]
- roadmap[]
- tasks[]
- feasibility (if required)

Be concise, factual, and actionable."""

    async def process(
        self,
        task_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process product manager request

        Args:
            task_id: Unique task ID
            payload: Input from orchestrator (TOON format expected)

        Returns:
            Agent output in TOON-compatible dict
        """
        try:
            # 1. Extract input
            prompt = payload.get("prompt", "")
            context_summaries = payload.get("context_summaries", [])
            require_feasibility = payload.get("require_feasibility_check", True)

            # 2. Prepare TOON input for model
            toon_input = toon_converter.json_to_toon({
                "product_request": {
                    "prompt": prompt,
                    "context_summaries": context_summaries[:5],  # Limit to top 5
                }
            })

            # 3. Check cache
            cache_key = f"pm:{hash(toon_input)}"
            cached = await cache_manager.get(cache_key)
            if cached:
                logger.info(f"Cache hit for task {task_id}")
                return cached

            # 4. Call LLM via OpenRouter
            response = await openrouter_client.chat_completion(
                model=settings.PRODUCT_MANAGER_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": toon_input}
                ],
                temperature=0.0,  # Factual outputs
                max_tokens=4096,
                timeout=settings.MODEL_CALL_TIMEOUT
            )

            # 5. Parse TOON response
            response_text = response["choices"][0]["message"]["content"]
            output = toon_converter.toon_to_json(response_text)

            # 6. Feasibility check if required
            if require_feasibility:
                output["feasibility"] = await self._check_feasibility(
                    task_id, output
                )

            # 7. Cache result
            await cache_manager.set(cache_key, output, ttl=settings.MODEL_CACHE_TTL)

            return output

        except Exception as e:
            logger.error(f"ProductManager agent failed: {e}")
            raise

    async def _check_feasibility(
        self,
        task_id: str,
        product_insight: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Engineer agent for feasibility check

        This is an internal agent-to-agent call
        """
        from app.agents.engineer import EngineerAgent

        engineer = EngineerAgent()

        # Prepare condensed TOON request
        feasibility_request = {
            "purpose": "feasibility_check",
            "feature_description": product_insight.get("title", ""),
            "roadmap_items": product_insight.get("roadmap", [])[:3],  # Top 3
            "constraints": ["memory <= 150MB", "render_cpu <= 20ms/frame"]
        }

        result = await engineer.process(
            task_id=f"{task_id}_feasibility",
            payload=feasibility_request
        )

        return {
            "feasible": result.get("result", {}).get("feasible", None),
            "constraints": result.get("result", {}).get("constraints", []),
            "engineer_notes": result.get("result", {}).get("feasibility_details", "")
        }

# Global instance
product_manager_agent = ProductManagerAgent()
```

---

## 📊 Complete Requirements (`requirements.txt`)

```txt
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0

# Database & Storage
supabase==2.3.0
psycopg2-binary==2.9.9

# Redis Queue
redis==5.0.1
upstash-redis==0.3.0

# LLM & AI
openai==1.6.1  # Compatible with OpenRouter
langchain==0.1.0
langgraph==0.0.20
anthropic==0.8.1

# Gmail API
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.110.0

# Security & Auth
pyjwt[crypto]==2.8.0
cryptography==41.0.7
pydantic[email]==2.5.3
pydantic-settings==2.1.0

# HTTP & Async
httpx==0.25.2
aiohttp==3.9.1
asyncio==3.4.3

# Data Processing
pyyaml==6.0.1  # For TOON format
ujson==5.9.0
orjson==3.9.10

# Monitoring & Logging
prometheus-client==0.19.0
sentry-sdk[fastapi]==1.39.1
structlog==23.2.0

# Rate Limiting & Caching
slowapi==0.1.9
aiocache==0.12.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2  # For testing

# Development
black==23.12.1
flake8==6.1.0
mypy==1.7.1
```

---

## 🔄 Worker Implementation (`app/workers/task_worker.py`)

```python
"""
Main Task Worker - Processes agent tasks from Redis queue
"""
import asyncio
import logging
from typing import Dict, Any
import redis.asyncio as redis
from app.config import get_settings
from app.database import get_supabase
from app.agents import (
    product_manager_agent,
    finance_manager_agent,
    marketing_strategist_agent,
    leadgen_scraper_agent,
    outbound_emailer_agent,
    booking_callprep_agent,
    engineer_agent
)

settings = get_settings()
logger = logging.getLogger(__name__)

# Agent registry
AGENT_HANDLERS = {
    "product_manager": product_manager_agent,
    "finance_manager": finance_manager_agent,
    "marketing_strategist": marketing_strategist_agent,
    "leadgen_scraper": leadgen_scraper_agent,
    "outbound_emailer": outbound_emailer_agent,
    "booking_callprep": booking_callprep_agent,
    "engineer": engineer_agent
}

class TaskWorker:
    """Background worker for processing agent tasks"""

    def __init__(self):
        self.redis_client = None
        self.supabase = get_supabase()
        self.running = False

    async def connect(self):
        """Connect to Redis"""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Worker connected to Redis")

    async def process_task(self, task_data: Dict[str, Any]) -> None:
        """
        Process a single task

        Args:
            task_data: Task payload from queue
        """
        task_id = task_data.get("task_id")
        agent_name = task_data.get("agent_name")
        input_payload = task_data.get("input")

        logger.info(f"Processing task {task_id} for agent {agent_name}")

        try:
            # 1. Update status to processing
            await self.supabase.table("agent_tasks").update({
                "status": "processing"
            }).eq("id", task_id).execute()

            # 2. Get agent handler
            agent = AGENT_HANDLERS.get(agent_name)
            if not agent:
                raise ValueError(f"Unknown agent: {agent_name}")

            # 3. Process with agent
            output = await agent.process(task_id, input_payload)

            # 4. Save output to database
            await self.supabase.table("agent_tasks").update({
                "status": "completed",
                "output": output,
                "completed_at": "now()"
            }).eq("id", task_id).execute()

            # 5. Save agent-specific outputs
            await self._save_agent_outputs(agent_name, task_id, output)

            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}", exc_info=True)

            # Update task with error
            await self.supabase.table("agent_tasks").update({
                "status": "failed",
                "error_message": str(e)
            }).eq("id", task_id).execute()

    async def _save_agent_outputs(
        self,
        agent_name: str,
        task_id: str,
        output: Dict[str, Any]
    ) -> None:
        """Save agent-specific outputs to appropriate tables"""

        if agent_name == "product_manager":
            await self.supabase.table("product_insights").insert({
                "task_id": task_id,
                "title": output.get("title"),
                "summary": output.get("summary"),
                "insights": output.get("insights"),
                "roadmap": output.get("roadmap"),
                "tasks": output.get("tasks"),
                "feasibility": output.get("feasibility"),
                "sources": output.get("sources")
            }).execute()

        elif agent_name == "booking_callprep":
            await self.supabase.table("call_scripts").insert({
                "intro": output.get("intro"),
                "top_questions": output.get("top_questions"),
                "demo_checklist": output.get("demo_checklist"),
                "objections_prepare": output.get("objections_prepare"),
                "closing_play": output.get("closing_play"),
                "followup_tasks": output.get("followup_tasks")
            }).execute()

        # Add other agent-specific saves...

    async def run(self):
        """Main worker loop"""
        await self.connect()
        self.running = True

        logger.info("Task worker started")

        while self.running:
            try:
                # Blocking pop from queue (30s timeout)
                task_json = await self.redis_client.brpop(
                    "agent_tasks_queue",
                    timeout=30
                )

                if task_json:
                    _, task_data = task_json
                    import json
                    task = json.loads(task_data)
                    await self.process_task(task)

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Backoff on error

    async def stop(self):
        """Stop worker gracefully"""
        self.running = False
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Worker stopped")

# Worker instance
worker = TaskWorker()
```

---

## 📮 Webhook Implementation (`app/webhooks/gmail.py`)

```python
"""
Gmail Webhook Handler - Receives Gmail push notifications via Pub/Sub
"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from app.utils.security import verify_webhook_signature
from app.utils.toon_converter import toon_converter
from app.database import get_supabase
from app.utils.gmail_client import gmail_client
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)
supabase = get_supabase()

@router.post("/webhook/gmail/push")
async def gmail_push_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Gmail push notification webhook (from Google Pub/Sub)

    Must acknowledge within 10 seconds
    Heavy processing done in background task
    """
    start_time = time.time()

    # 1. Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("x-webhook-signature", "")

    # 2. Verify HMAC signature
    if not verify_webhook_signature(body, signature):
        logger.warning("Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 3. Parse payload
    try:
        payload = json.loads(body)
        pubsub_message = payload.get("message", {})
        message_id = pubsub_message.get("messageId")

        if not message_id:
            raise ValueError("Missing messageId")

    except Exception as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    # 4. Log webhook reception
    await supabase.table("webhook_events").insert({
        "external_id": message_id,
        "endpoint": "/webhook/gmail/push",
        "payload": payload,
        "headers": dict(request.headers),
        "signature_valid": True,
        "processing_status": "accepted"
    }).execute()

    # 5. Enqueue background processing
    background_tasks.add_task(
        process_gmail_message,
        message_id=message_id
    )

    # 6. Return 200 immediately (< 1 second)
    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "status": "accepted",
        "message_id": message_id,
        "processing": "background",
        "duration_ms": duration_ms
    }

async def process_gmail_message(message_id: str):
    """
    Background task to fetch and process Gmail message
    """
    try:
        # 1. Fetch full message from Gmail API
        message = await gmail_client.get_message(message_id)

        if not message:
            logger.warning(f"Message {message_id} not found")
            return

        # 2. Extract email data
        email_data = {
            "external_id": message_id,
            "from": message.get("from"),
            "to": message.get("to", []),
            "subject": message.get("subject", ""),
            "body_text": message.get("body_text", ""),
            "thread_id": message.get("thread_id"),
            "received_at": message.get("received_at")
        }

        # 3. Convert to TOON for logging
        toon_repr = toon_converter.json_to_toon({"email": email_data})
        logger.info(f"Processed email:\n{toon_repr}")

        # 4. Save to email_events
        await supabase.table("email_events").insert({
            **email_data,
            "direction": "inbound",
            "status": "received",
            "raw": message
        }).execute()

        # 5. Match to lead
        lead = await _match_lead_by_email(email_data["from"])

        if lead:
            # Update lead history
            history = lead.get("history", [])
            history.append({
                "event": "email_received",
                "email_id": message_id,
                "subject": email_data["subject"],
                "at": email_data["received_at"]
            })

            await supabase.table("leads").update({
                "history": history,
                "last_contacted_at": email_data["received_at"]
            }).eq("id", lead["id"]).execute()

            # 6. Check auto-reply rules
            await _check_auto_reply_rules(lead, email_data)

        # Update webhook event status
        await supabase.table("webhook_events").update({
            "processing_status": "processed"
        }).eq("external_id", message_id).execute()

    except Exception as e:
        logger.error(f"Failed to process Gmail message {message_id}: {e}")
        await supabase.table("webhook_events").update({
            "processing_status": "failed",
            "error_message": str(e)
        }).eq("external_id", message_id).execute()

async def _match_lead_by_email(email: str):
    """Find lead by email address"""
    result = await supabase.table("leads").select("*").eq(
        "email", email
    ).limit(1).execute()

    return result.data[0] if result.data else None

async def _check_auto_reply_rules(lead: dict, email_data: dict):
    """Check if auto-reply should be sent"""
    # Implement auto-reply logic here
    # This would enqueue an outbound_emailer task
    pass
```

---

## 🐳 Docker & Deployment

### `docker-compose.yml` (Local Development)

```yaml
version: '3.8'

services:
  # FastAPI Orchestrator
  orchestrator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - redis
    volumes:
      - ./app:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Task Workers
  worker:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - redis
    command: python -m app.workers.task_worker
    deploy:
      replicas: 2

  # Redis Queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Puppeteer Scraper
  scraper:
    build: ./scrapers
    environment:
      - API_URL=http://orchestrator:8000
    depends_on:
      - orchestrator

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

volumes:
  redis_data:
  prometheus_data:
```

### Production `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 🎯 Next Steps

### Phase 1: Core Setup ✅
- [x] Database schema created
- [x] Architecture documented
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set up Supabase project and run schema
- [ ] Configure environment variables

### Phase 2: Implementation
- [ ] Implement all agent handlers (`app/agents/`)
- [ ] Build webhook endpoints (`app/webhooks/`)
- [ ] Create worker processes (`app/workers/`)
- [ ] Implement utilities (TOON, security, clients)

### Phase 3: Integration
- [ ] Gmail API setup with Pub/Sub
- [ ] OpenRouter integration testing
- [ ] Puppeteer scraper container
- [ ] Redis queue testing

### Phase 4: Production
- [ ] Comprehensive testing
- [ ] Prometheus metrics
- [ ] Sentry error tracking
- [ ] Deploy to Render
- [ ] Connect frontend

---

## 📚 Key References

- **Prompt.md**: Complete specification
- **supabase_schema.sql**: Database structure
- **OpenRouter Docs**: https://openrouter.ai/docs
- **Gmail API**: https://developers.google.com/gmail/api
- **LangChain**: https://python.langchain.com/docs

---

This guide provides the complete architecture for a production-grade AI Agent Team backend. Follow the implementation pattern shown above for all components.
