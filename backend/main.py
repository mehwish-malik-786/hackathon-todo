from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tasks
from database import create_db_tables
from config import get_settings

settings = get_settings()

app = FastAPI(
    title="Hackathon TODO API",
    description="Simple task management API for hackathon demo",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_db_tables()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Hackathon TODO API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
