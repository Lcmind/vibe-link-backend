"""Pydantic models for poster generation."""

from pydantic import BaseModel, HttpUrl, Field


class PosterRequest(BaseModel):
    """Request model for poster creation."""
    url: str = Field(..., description="Website URL to analyze")


class PosterResponse(BaseModel):
    """Response model for generated poster."""
    poster_url: str = Field(..., description="URL of the generated poster image")
    analysis: str = Field(..., description="AI analysis of the website")


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")
