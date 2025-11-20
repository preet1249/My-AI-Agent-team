"""
Main FastAPI Application - AI Agent Team Backend
Orchestrates 7 AI agents with webhooks, workers, and database
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Import agents
from app.agents.product_manager import product_manager_agent
from app.agents.finance_manager import finance_manager_agent
from app.agents.marketing_strategist import marketing_strategist_agent
from app.agents.leadgen_scraper import leadgen_scraper_agent
from app.agents.outbound_emailer import outbound_emailer_agent
from app.agents.booking_callprep import booking_callprep_agent
from app.agents.engineer import engineer_agent
from app.agents.personal_assistant import personal_assistant_agent

# Import webhooks
from app.webhooks.email_webhook import router as email_webhook_router
from app.webhooks.calendar_webhook import router as calendar_webhook_router
from app.webhooks.scrape_webhook import router as scrape_webhook_router
from app.webhooks.task_webhook import router as task_webhook_router

# Import utilities
from app.database import supabase_client
from app.redis_client import redis_queue
from app.utils.security import verify_internal_auth
from app.utils.web_search import web_searcher
from app.utils.agent_router import agent_router, AGENT_NAMES, AGENT_ID_TO_NAME
from app.utils.openrouter_client import openrouter_client
from app.utils.conversation_memory import conversation_memory
from app.utils.marketing_platforms import get_all_platforms
from app.config import get_settings

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AI Agent Team Backend",
    description="Orchestrator for 7 AI agents with webhooks and workers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook routers
app.include_router(email_webhook_router, tags=["webhooks"])
app.include_router(calendar_webhook_router, tags=["webhooks"])
app.include_router(scrape_webhook_router, tags=["webhooks"])
app.include_router(task_webhook_router, tags=["webhooks"])


# Request/Response models
class AgentRequest(BaseModel):
    user_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None


class LeadGenRequest(BaseModel):
    user_id: str
    target_urls: List[str]
    criteria: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None


class EmailCampaignRequest(BaseModel):
    user_id: str
    lead_ids: List[str]
    campaign_id: Optional[str] = None
    template: Optional[str] = None
    external_id: Optional[str] = None


class CallPrepRequest(BaseModel):
    user_id: str
    lead_id: Optional[str] = None
    meeting_type: str = "discovery"
    scheduled_time: Optional[str] = None
    external_id: Optional[str] = None


class EngineerRequest(BaseModel):
    user_id: str
    prompt: str
    language: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    external_id: Optional[str] = None


class ThinkRequest(BaseModel):
    user_id: str
    query: str
    agent_name: Optional[str] = None  # Which agent to use for thinking
    max_results: int = 5  # How many websites to search/scrape


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "redis": "connected" if redis_queue else "disconnected",
        "database": "connected" if supabase_client else "disconnected"
    }

# Deploy verification endpoint
@app.get("/verify")
async def verify_deployment():
    """Verify latest code is deployed"""
    return {
        "deployed": True,
        "version": "2.0.0",
        "commit": "LATEST",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "✅ Latest code is deployed successfully!"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Agent Team Backend",
        "version": "2.0.0",
        "agents": [
            "product_manager (Alex)",
            "finance_manager (Marcus)",
            "marketing_strategist (Ryan)",
            "leadgen_scraper (Jake)",
            "outbound_emailer (Chris)",
            "booking_callprep (Daniel)",
            "engineer (Kevin)",
            "personal_assistant (Sophia)"
        ],
        "features": [
            "Agent-to-agent communication",
            "Think mode with web scraping",
            "@mention routing"
        ]
    }


# Agent endpoints
@app.post("/api/agents/product-manager")
async def product_manager_endpoint(request: AgentRequest):
    """
    Product Manager Agent
    Analyzes trends, creates insights, manages roadmaps
    """
    try:
        result = await product_manager_agent.process(
            user_id=request.user_id,
            prompt=request.prompt,
            context=request.context,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Product Manager endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/finance-manager")
async def finance_manager_endpoint(request: AgentRequest):
    """
    Finance Manager Agent
    Analyzes finances, tracks expenses, provides insights
    """
    try:
        result = await finance_manager_agent.process(
            user_id=request.user_id,
            prompt=request.prompt,
            context=request.context,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Finance Manager endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/marketing-strategist")
async def marketing_strategist_endpoint(request: AgentRequest):
    """
    Marketing Strategist Agent
    Creates campaigns, analyzes performance, optimizes strategies
    """
    try:
        result = await marketing_strategist_agent.process(
            user_id=request.user_id,
            prompt=request.prompt,
            context=request.context,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Marketing Strategist endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/leadgen-scraper")
async def leadgen_scraper_endpoint(request: LeadGenRequest):
    """
    Lead Generation Scraper Agent
    Finds leads via web scraping with politeness
    """
    try:
        result = await leadgen_scraper_agent.process(
            user_id=request.user_id,
            target_urls=request.target_urls,
            criteria=request.criteria,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Lead Gen Scraper endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/leadgen")
async def leadgen_prompt_endpoint(request: AgentRequest):
    """
    Lead Generation Agent - Natural Language Interface
    Accepts prompts like "find 10 leads in Austin tech companies"
    Auto-saves leads to spreadsheet/database
    """
    try:
        # Parse the prompt to extract search parameters
        prompt = request.prompt.lower()

        # Extract number of leads requested
        import re
        num_match = re.search(r'(\d+)\s*leads?', prompt)
        max_leads = int(num_match.group(1)) if num_match else 10

        # Build search query from prompt
        # Remove common words to get the search query
        search_query = request.prompt
        for word in ['find', 'get', 'search', 'leads', 'lead', 'for', 'me', 'please', str(max_leads)]:
            search_query = re.sub(rf'\b{word}\b', '', search_query, flags=re.IGNORECASE)
        search_query = ' '.join(search_query.split())  # Clean whitespace

        # Add "company contact email" to improve results
        search_query = f"{search_query} company contact email"

        logger.info(f"Lead Gen processing: '{request.prompt}' -> search: '{search_query}', max: {max_leads}")

        # Call the lead gen agent with search query
        result = await leadgen_scraper_agent.process(
            user_id=request.user_id,
            search_query=search_query,
            criteria={"max_leads": max_leads},
            external_id=request.external_id
        )

        # Format response
        leads = result.get("leads", [])

        if leads:
            response_text = f"Found {len(leads)} leads:\n\n"
            for i, lead in enumerate(leads, 1):
                response_text += f"**{i}. {lead.get('company', 'Unknown')}**\n"
                if lead.get('name'):
                    response_text += f"   - Name: {lead['name']}\n"
                if lead.get('email'):
                    response_text += f"   - Email: {lead['email']}\n"
                metadata = lead.get('metadata', {})
                if metadata.get('role'):
                    response_text += f"   - Role: {metadata['role']}\n"
                if metadata.get('company_description'):
                    response_text += f"   - About: {metadata['company_description'][:100]}...\n"
                response_text += f"   - Score: {lead.get('score', 0)}/100\n\n"

            response_text += f"\n✅ All {len(leads)} leads have been saved to your Spreadsheet!"
        else:
            response_text = "No leads found for your search. Try a different location or industry."

        return {
            "success": True,
            "data": {
                "response": response_text,
                "leads_found": len(leads),
                "leads": leads
            }
        }

    except Exception as e:
        logger.error(f"Lead Gen prompt endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/outbound-emailer")
async def outbound_emailer_endpoint(request: EmailCampaignRequest):
    """
    Outbound Emailer Agent
    Sends personalized emails via Gmail API
    """
    try:
        result = await outbound_emailer_agent.process(
            user_id=request.user_id,
            lead_ids=request.lead_ids,
            campaign_id=request.campaign_id,
            template=request.template,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Outbound Emailer endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/booking-callprep")
async def booking_callprep_endpoint(request: CallPrepRequest):
    """
    Booking & Call Prep Agent
    Schedules meetings and generates call scripts
    """
    try:
        result = await booking_callprep_agent.process(
            user_id=request.user_id,
            lead_id=request.lead_id,
            meeting_type=request.meeting_type,
            scheduled_time=request.scheduled_time,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Booking Call Prep endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/engineer")
async def engineer_endpoint(request: EngineerRequest):
    """
    Engineer Agent
    Writes code, debugs, provides technical solutions
    """
    try:
        result = await engineer_agent.process(
            user_id=request.user_id,
            prompt=request.prompt,
            language=request.language,
            context=request.context,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Engineer endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/personal-assistant")
async def personal_assistant_endpoint(request: AgentRequest):
    """
    Personal AI Assistant - Sophia
    Has access to ALL app data, can coordinate with other agents
    Most intelligent agent with full context awareness
    """
    try:
        result = await personal_assistant_agent.process(
            user_id=request.user_id,
            prompt=request.prompt,
            context=request.context,
            external_id=request.external_id
        )
        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Personal Assistant endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/think")
async def think_endpoint(request: ThinkRequest):
    """
    THINK Mode - Search web, scrape content, analyze with NVIDIA NeMo

    When user clicks "Think":
    1. Searches DuckDuckGo (FREE, unlimited)
    2. Scrapes top websites/blogs
    3. Sends to NVIDIA NeMo for intelligent analysis
    4. Returns structured, perfect answer

    Agent automatically determines if they need other agents' input.
    """
    try:
        logger.info(f"Think mode activated for: {request.query}")

        # Step 1: Search DuckDuckGo and scrape content
        search_results = await web_searcher.search_and_scrape(
            query=request.query,
            max_results=request.max_results,
            scrape_content=True
        )

        # Step 2: Combine all scraped content
        combined_content = ""
        sources = []

        for result in search_results:
            if result.get("scraped") and result.get("content"):
                combined_content += f"\n\n=== {result['title']} ({result['url']}) ===\n"
                combined_content += result['content']
                sources.append({
                    "title": result['title'],
                    "url": result['url']
                })

        # Step 3: Determine which agent to use (or use specified)
        agent_to_use = request.agent_name
        if not agent_to_use:
            # Auto-detect agent based on query
            detected = agent_router.detect_agent_needed(request.query)
            agent_to_use = detected if detected else "product_manager"

        # Convert agent name to ID if using @mention
        if agent_to_use.lower() in AGENT_NAMES:
            agent_to_use = AGENT_NAMES[agent_to_use.lower()]

        logger.info(f"Using agent: {agent_to_use} ({AGENT_ID_TO_NAME.get(agent_to_use, agent_to_use)})")

        # Step 4: Build enhanced prompt with scraped data
        enhanced_prompt = f"""
{request.query}

I have gathered the following information from the web:

{combined_content[:10000]}

Please analyze this information and provide a structured, intelligent, and accurate answer.
Make it perfect and valuable.
"""

        # Step 5: Send to appropriate agent with web context
        context = {
            "web_search_results": search_results,
            "sources": sources,
            "think_mode": True
        }

        # Call the appropriate agent
        agents = {
            "product_manager": product_manager_agent,
            "finance_manager": finance_manager_agent,
            "marketing_strategist": marketing_strategist_agent,
            "engineer": engineer_agent,
            "personal_assistant": personal_assistant_agent
        }

        agent = agents.get(agent_to_use, product_manager_agent)

        result = await agent.process(
            user_id=request.user_id,
            prompt=enhanced_prompt,
            context=context
        )

        return {
            "success": True,
            "data": {
                **result,
                "agent_used": AGENT_ID_TO_NAME.get(agent_to_use, agent_to_use),
                "sources": sources,
                "search_results_count": len(search_results)
            }
        }

    except Exception as e:
        logger.error(f"Think endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Query endpoints
@app.get("/api/tasks/{user_id}")
async def get_user_tasks(user_id: str, limit: int = 20):
    """Get user's agent tasks"""
    try:
        result = supabase_client.table("agent_tasks") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"success": True, "data": result.data}

    except Exception as e:
        logger.error(f"Get tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads/{user_id}")
async def get_user_leads(user_id: str, limit: int = 50):
    """Get user's leads"""
    try:
        result = supabase_client.table("leads") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("score", desc=True) \
            .limit(limit) \
            .execute()

        return {"success": True, "data": result.data}

    except Exception as e:
        logger.error(f"Get leads error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights/{user_id}")
async def get_user_insights(user_id: str, limit: int = 20):
    """Get user's product insights"""
    try:
        result = supabase_client.table("product_insights") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"success": True, "data": result.data}

    except Exception as e:
        logger.error(f"Get insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/campaigns/{user_id}")
async def get_user_campaigns(user_id: str, limit: int = 20):
    """Get user's marketing campaigns"""
    try:
        result = supabase_client.table("campaigns") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return {"success": True, "data": result.data}

    except Exception as e:
        logger.error(f"Get campaigns error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts/{user_id}")
async def get_user_alerts(user_id: str, read: Optional[bool] = None):
    """Get user's alerts"""
    try:
        query = supabase_client.table("alerts") \
            .select("*") \
            .eq("user_id", user_id)

        if read is not None:
            query = query.eq("read", read)

        result = query.order("created_at", desc=True).limit(50).execute()

        return {"success": True, "data": result.data}

    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Marketing Platforms Endpoint =====

@app.get("/api/marketing/platforms")
async def get_marketing_platforms():
    """Get list of available marketing platforms for content creation"""
    try:
        platforms = get_all_platforms()
        return {
            "success": True,
            "data": platforms
        }
    except Exception as e:
        logger.error(f"Get marketing platforms error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Conversation Endpoints =====

class ConversationCreateRequest(BaseModel):
    user_id: str
    title: Optional[str] = "New Chat"
    agent_type: Optional[str] = None


@app.post("/api/conversations")
async def create_conversation(request: ConversationCreateRequest):
    """Create a new conversation"""
    try:
        conversation_id = await conversation_memory.create_conversation(
            user_id=request.user_id,
            title=request.title,
            agent_type=request.agent_type
        )

        if not conversation_id:
            raise HTTPException(status_code=500, detail="Failed to create conversation")

        return {
            "success": True,
            "data": {"conversation_id": conversation_id}
        }

    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversations/{user_id}")
async def get_conversations(user_id: str, limit: int = 20):
    """Get list of conversations for a user"""
    try:
        conversations = await conversation_memory.get_conversations(user_id, limit)

        return {
            "success": True,
            "data": conversations
        }

    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all messages"""
    try:
        conversation = await conversation_memory.get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {
            "success": True,
            "data": conversation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/conversation/{conversation_id}")
async def update_conversation(conversation_id: str, title: Optional[str] = None):
    """Update conversation metadata"""
    try:
        success = await conversation_memory.update_conversation(conversation_id, title)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update conversation")

        return {
            "success": True,
            "data": {"conversation_id": conversation_id}
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Multi-Agent Communication Endpoint =====

class MultiAgentRequest(BaseModel):
    user_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None


# Agent mapping for multi-agent calls
AGENT_INSTANCES = {
    "product_manager": product_manager_agent,
    "finance_manager": finance_manager_agent,
    "marketing_strategist": marketing_strategist_agent,
    "engineer": engineer_agent,
    "personal_assistant": personal_assistant_agent,
    "booking_callprep": booking_callprep_agent,
}


@app.post("/api/multi-agent")
async def multi_agent_endpoint(request: MultiAgentRequest):
    """
    Multi-Agent Communication
    Handles @mentions between agents like "@alex ask @kevin is this possible?"

    Flow:
    1. Parse @mentions from prompt
    2. First agent asks the second agent
    3. Second agent responds
    4. First agent synthesizes final response
    """
    try:
        # Parse @mentions
        mentioned_agents = agent_router.parse_mentions(request.prompt)

        if len(mentioned_agents) < 2:
            # Not enough mentions, use default agent
            raise HTTPException(
                status_code=400,
                detail="Please mention at least 2 agents (e.g., '@alex ask @kevin')"
            )

        logger.info(f"Multi-agent request with agents: {mentioned_agents}")

        # Get first two agents
        primary_agent_id = mentioned_agents[0]
        secondary_agent_id = mentioned_agents[1]

        primary_name = AGENT_ID_TO_NAME.get(primary_agent_id, primary_agent_id)
        secondary_name = AGENT_ID_TO_NAME.get(secondary_agent_id, secondary_agent_id)

        # Get agent instances
        primary_agent = AGENT_INSTANCES.get(primary_agent_id)
        secondary_agent = AGENT_INSTANCES.get(secondary_agent_id)

        if not primary_agent or not secondary_agent:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent mentioned. Available: {list(AGENT_ID_TO_NAME.values())}"
            )

        # Extract the actual question (remove @mentions)
        question = request.prompt
        for name in AGENT_NAMES.keys():
            question = question.replace(f"@{name}", "").strip()

        # Remove common phrases
        question = question.replace("ask", "").replace("tell", "").strip()

        # Step 1: Secondary agent answers the question
        logger.info(f"Step 1: {secondary_name} processing question")

        secondary_prompt = f"""You are {secondary_name}. Another team member ({primary_name}) is asking you:

{question}

Please provide a clear, helpful answer based on your expertise."""

        secondary_result = await secondary_agent.process(
            user_id=request.user_id,
            prompt=secondary_prompt,
            context={"multi_agent": True, "requesting_agent": primary_agent_id}
        )

        secondary_response = secondary_result.get("response", "No response from agent")

        # Step 2: Primary agent synthesizes the response
        logger.info(f"Step 2: {primary_name} synthesizing response")

        primary_prompt = f"""You are {primary_name}. You asked {secondary_name} the following question:

"{question}"

{secondary_name}'s response:
{secondary_response}

Now synthesize this information and provide a final, helpful response to the user.
Acknowledge {secondary_name}'s input and add your own perspective if relevant."""

        primary_result = await primary_agent.process(
            user_id=request.user_id,
            prompt=primary_prompt,
            context={"multi_agent": True, "consulted_agent": secondary_agent_id}
        )

        primary_response = primary_result.get("response", "No response from agent")

        # Format final response
        final_response = f"""**{primary_name}** asked **{secondary_name}**: {question}

---

**{secondary_name}'s response:**
{secondary_response}

---

**{primary_name}'s synthesis:**
{primary_response}"""

        return {
            "success": True,
            "data": {
                "response": final_response,
                "agents_involved": [primary_agent_id, secondary_agent_id],
                "primary_agent": primary_name,
                "secondary_agent": secondary_name
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-agent endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Agent Team Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Backend ready!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Agent Team Backend...")
    await redis_queue.close()
    logger.info("Shutdown complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )
