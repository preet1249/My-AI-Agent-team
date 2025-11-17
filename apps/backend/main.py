"""
FastAPI Orchestrator API
Main entry point for the AI Agent Team backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Agent Team API",
    description="Orchestrator API for multi-agent AI system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI Agent Team API is running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "redis": "connected",  # TODO: Add actual Redis check
        "database": "connected",  # TODO: Add actual DB check
    }

# Import routers
from app.routes import agents, tasks, sheets, calendar, webhooks

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(sheets.router, prefix="/api/sheets", tags=["sheets"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
