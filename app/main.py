"""FastAPI application initialization."""

from fastapi import FastAPI
from app.core.config import settings
from app.core.security import configure_cors
from app.api.routes import poster


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        debug=settings.debug,
    )
    
    # Configure CORS with strict origin control
    configure_cors(app)
    
    # Register routers
    app.include_router(poster.router)
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "VIBE_LINK API",
            "version": "1.0.0",
            "status": "operational"
        }
    
    return app


# Create app instance
app = create_app()
