"""
SchemaSense Generator - FastAPI Backend

Standalone FastAPI backend for automated CSV schema analysis
and MySQL DDL generation with AI-powered documentation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.routes import router


def create_app() -> FastAPI:
    """Set up the FastAPI app with CORS and routes"""
    app = FastAPI(
        title=f"{settings.app_name} API",
        description="REST API for automated CSV schema inference and MySQL DDL generation",
        version=settings.app_version,
        docs_url="/docs",    # Swagger UI at /docs
        redoc_url="/redoc"   # ReDoc at /redoc
    )
    
    # CORS setup for our React frontend running on :3000
    # Pretty permissive but fine for development - would lock down in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,  # configured in settings
        allow_credentials=True,
        allow_methods=["*"],  # allow all HTTP methods
        allow_headers=["*"],  # allow all headers
    )
    
    # Wire up all our API endpoints
    app.include_router(router)
    
    return app


# Create the app instance that uvicorn will serve
app = create_app()


@app.get("/")
async def root():
    """Just tells you what this API does and where to find the docs"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "FastAPI backend for CSV schema analysis",
        "docs": "/docs",        # interactive API docs
        "health": "/api/health" # health check
    }


if __name__ == "__main__":
    # Direct execution for development - in production you'd use gunicorn or similar
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,  # auto-reload when files change in debug mode
        log_level="info"
    )