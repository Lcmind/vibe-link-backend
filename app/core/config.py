"""Application configuration and environment variables."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    hf_token: str = os.getenv("HF_TOKEN", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    imgbb_key: str = os.getenv("IMGBB_KEY", "")
    
    # CORS Origins - 환경에 따라 동적 설정
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://vibe-link.vercel.app",  # 향후 프로덕션 도메인
    ]
    
    # Application Settings
    app_title: str = "VIBE_LINK API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Hugging Face Models
    flux_model: str = "black-forest-labs/FLUX.1-schnell"
    flux_steps: int = 4
    
    # Gemini Model
    gemini_model: str = "gemini-2.0-flash-exp"
    
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
        case_sensitive = False


settings = Settings()
