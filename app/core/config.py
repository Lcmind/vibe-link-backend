"""Application configuration and environment variables."""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys - pydantic_settings reads from env automatically
    hf_token: str = Field(default="", alias="HF_TOKEN")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    imgbb_key: str = Field(default="", alias="IMGBB_KEY")
    
    # CORS Origins - 환경에 따라 동적 설정
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
        "https://vibe-link.vercel.app",  # 향후 프로덕션 도메인
    ]
    
    # Application Settings
    app_title: str = "VIBE_LINK API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Hugging Face Models - use stable-diffusion instead of FLUX
    flux_model: str = "black-forest-labs/FLUX.1-schnell"
    flux_steps: int = 20
    
    # Gemini Model - 2.5-flash
    gemini_model: str = "gemini-1.5-flash"
    
    # Pyppeteer Settings
    puppeteer_executable_path: str = "/usr/bin/chromium"
    puppeteer_args: List[str] = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ]
    
    class Config:
        env_file = ".env"
        populate_by_name = True  # Allow field aliases
        case_sensitive = False


settings = Settings()
