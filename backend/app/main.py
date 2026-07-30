"""
StreamGuard AI - Main Application Entry Point
FastAPI app with all routes, middleware, and startup logic.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import stream, superchat, websocket
from app.api.dependencies import init_services

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic."""
    settings = get_settings()
    setup_logging(debug=settings.app_debug)
    
    logger.info("=" * 50)
    logger.info("🛡️  StreamGuard AI - Starting Up")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Debug: {settings.app_debug}")
    logger.info("=" * 50)
    
    # Initialize all services
    init_services()
    
    yield  # App is running
    
    # Shutdown
    logger.info("🛡️  StreamGuard AI - Shutting Down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="StreamGuard AI",
        description="AI co-pilot for live stream super chat management",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routes
    app.include_router(stream.router, prefix="/api")
    app.include_router(superchat.router, prefix="/api")
    app.include_router(websocket.router)
    
    # Health check
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "StreamGuard AI",
            "version": settings.app_version,
        }
    
    return app


app = create_app()
