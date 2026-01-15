"""Security configurations including CORS."""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.core.config import settings


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with strict origin control.
    
    Only allows requests from specified frontend domains.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,  # 프론트엔드 도메인만 허용
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )
