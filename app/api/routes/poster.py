"""Poster generation API endpoints."""

from fastapi import APIRouter, HTTPException
from app.schemas.poster import PosterRequest, PosterResponse
from app.services.screenshot import capture_screenshot
from app.core.config import settings
from app.services.gemini import analyze_with_gemini
from app.services.groq import analyze_with_groq
from app.services.flux import generate_poster
from app.services.imgbb import upload_to_imgbb

router = APIRouter(prefix="/api", tags=["poster"])


@router.post("/create", response_model=PosterResponse)
async def create_poster(request: PosterRequest):
    """
    Generate a brand vibe poster from a website URL.
    
    Pipeline:
    1. Capture website screenshot
    2. Analyze with Gemini Vision AI
    3. Generate poster with Flux AI (includes brand text in image)
    4. Upload to ImgBB for permanent hosting
    
    Note: Flux generates the brand name text directly in the image.
    No overlay needed - text is part of the generated design.
    
    Args:
        request: PosterRequest with URL
        
    Returns:
        PosterResponse with poster URL and analysis
    """
    try:
        # Step 1: Capture screenshot
        screenshot_path = await capture_screenshot(request.url)
        
        # Step 2: 분석 모델 자동 선택
        if settings.analysis_model == "groq":
            analysis = await analyze_with_groq(screenshot_path)
        else:
            analysis = await analyze_with_gemini(screenshot_path)
        
        # Step 3: Generate poster with Flux (brand text included in prompt)
        poster_path = await generate_poster(analysis)
        
        # Step 4: Upload to ImgBB (no overlay - Flux generates text)
        poster_url = await upload_to_imgbb(poster_path)
        
        brand_name = analysis.get('brand_name', 'BRAND')
        
        return PosterResponse(
            poster_url=poster_url,
            analysis=f"{brand_name}: {analysis.get('what_they_provide', '')}"
        )
        
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR in /api/create: {error_detail}")  # Log to container
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "VIBE_LINK API",
        "version": "1.0.0"
    }
