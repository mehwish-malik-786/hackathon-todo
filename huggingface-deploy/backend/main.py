"""
Hackathon Todo API - Production-Ready FastAPI Application.

Features:
- Task CRUD operations (Phase II)
- AI Chatbot with natural language (Phase III)
- HuggingFace Inference API integration
- Async request handling
- Comprehensive error handling
- WSL Ubuntu compatible

Usage:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Environment Variables:
    See .env.example for configuration options
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import tasks, chat
from database import create_db_tables
from config import get_settings
from services.ai_agent import initialize_ai_agent, shutdown_ai_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for async startup/shutdown.

    Handles:
    - Database table creation
    - AI agent initialization
    - Resource cleanup on shutdown
    """
    # === Startup ===
    logger.info("🚀 Starting Hackathon Todo API...")

    # Create database tables
    try:
        create_db_tables()
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # Initialize AI agent
    settings = get_settings()
    if settings.is_hf_api_enabled():
        try:
            await initialize_ai_agent(
                hf_token=settings.hf_token,
                model_id=settings.get_hf_model_id()
            )
            logger.info(f"✅ AI Chatbot initialized (HF API mode: {settings.get_hf_model_id()})")
        except Exception as e:
            logger.warning(f"⚠️  AI initialization failed: {e}")
            logger.warning("   Falling back to rule-based mode")
    else:
        logger.info("⚠️  HF_TOKEN not configured. Using rule-based AI mode.")
        await initialize_ai_agent()

    logger.info("✅ Application startup complete")

    yield

    # === Shutdown ===
    logger.info("🛑 Shutting down Hackathon Todo API...")

    # Cleanup AI agent resources
    try:
        await shutdown_ai_agent()
        logger.info("✅ AI agent resources cleaned up")
    except Exception as e:
        logger.warning(f"⚠️  AI cleanup error: {e}")

    logger.info("✅ Application shutdown complete")


# Create FastAPI application
settings = get_settings()

app = FastAPI(
    title="Hackathon TODO API",
    description="Production-ready task management API with AI Chatbot support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router)
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint with API information.

    Returns:
        API metadata and documentation links
    """
    return {
        "message": "Hackathon TODO API",
        "version": "1.0.0",
        "features": [
            "Task CRUD operations",
            "AI Chatbot (natural language)",
            "Conversation history"
        ],
        "docs": "/docs",
        "health": "/health",
        "chat": "/api/chat",
    }


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    return {"status": "healthy"}


@app.get("/ready")
def ready():
    """
    Readiness check endpoint.

    Returns:
        Service readiness status with AI mode
    """
    from services.ai_agent import get_ai_agent

    ai_agent = get_ai_agent()
    return {
        "status": "ready",
        "ai_mode": ai_agent.mode.value if ai_agent._initialized else "not_initialized",
    }
