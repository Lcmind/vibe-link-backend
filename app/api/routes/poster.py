"""Poster generation API endpoints."""

from fastapi import APIRouter, HTTPException
from app.schemas.poster import PosterRequest, PosterResponse
from app.services.screenshot import capture_screenshot
from app.services.gemini import analyze_with_gemini
from app.services.flux import generate_poster
from app.services.overlay import add_brand_overlay
from app.services.imgbb import upload_to_imgbb

router = APIRouter(prefix="/api", tags=["poster"])


@router.post("/create", response_model=PosterResponse)
async def create_poster(request: PosterRequest):
    """
    Generate a brand vibe poster from a website URL.
    
    Pipeline:
    1. Capture website screenshot
    2. Analyze with Gemini Vision AI
    3. Generate poster with Flux AI
    4. Add brand overlay with Pillow
    5. Upload to ImgBB for permanent hosting
    
    Args:
        request: PosterRequest with URL
        
    Returns:
        PosterResponse with poster URL and analysis
    """
    try:
        # Step 1: Capture screenshot
        screenshot_path = await capture_screenshot(request.url)
        
        # Step 2: Analyze with Gemini
        analysis = await analyze_with_gemini(screenshot_path)
        
        # Step 3: Generate poster with Flux
        poster_path = await generate_poster(analysis)
        
        # Step 4: Add brand name overlay with Pillow
        brand_name = analysis.get('brand_name', 'BRAND')
        color_palette = analysis.get('color_palette', {})
        primary_color = color_palette.get('primary', '#FFFFFF')
        
        final_poster_path = add_brand_overlay(poster_path, brand_name, primary_color)
        
        # Step 5: Upload to ImgBB
        poster_url = await upload_to_imgbb(final_poster_path)
        
        return PosterResponse(
            poster_url=poster_url,
            analysis=f"{brand_name}: {analysis.get('what_they_do', '')}"
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
