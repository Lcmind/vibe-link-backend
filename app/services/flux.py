"""Flux AI image generation service."""

import httpx
from PIL import Image
import io
from app.core.config import settings


async def generate_poster(analysis: dict) -> str:
    """
    Generate a poster using Flux AI based on analysis.
    
    Args:
        analysis: Analysis results from Gemini
        
    Returns:
        str: Path to the generated poster image
        
    Raises:
        Exception: If generation fails
    """
    # Construct detailed prompt for Flux
    brand_name = analysis.get('brand_name', 'BRAND')
    core_offering = analysis.get('core_offering', 'innovative service')
    visual_scene = analysis.get('visual_scene', 'modern abstract background')
    brand_text_material = analysis.get('brand_text_material', 'glowing neon letters')
    primary_color = analysis.get('primary_color', '#000000')
    secondary_colors = analysis.get('secondary_colors', [])
    keywords = ', '.join(analysis.get('keywords', ['modern', 'professional']))
    
    # Build color description
    if secondary_colors and len(secondary_colors) > 0:
        color_desc = f"multi-colored ({', '.join(secondary_colors)})"
    else:
        color_desc = f"in {primary_color} color scheme"
    
    prompt = f"""
A high-end vertical commercial poster (9:16 aspect ratio, 768x1344px).

THE HERO TEXT (BRAND NAME AS THE CENTERPIECE):
The text '{brand_name}' is the main focal point of the image.
The text is rendered as: {brand_text_material}
The text colors: {color_desc}
Typography: Bold, big, legible, positioned prominently (center or top-center).

THE VISUAL SCENE (REPRESENTING WHAT THEY DO):
Core business: {core_offering}
Background environment: {visual_scene}

STYLE & ATMOSPHERE:
- Cinematic commercial photography
- Keywords: {keywords}
- Volumetric lighting, dramatic depth of field
- Clean composition, professional aesthetic

TECHNICAL QUALITY:
- 8K resolution, Unreal Engine 5 render
- Octane Render, Ray Tracing, Super-Resolution
- Award-winning commercial poster design

STRICT RULES:
- NO UI elements, NO browser bars, NO website screenshots
- Text must be in ENGLISH only (no Korean characters)
- Focus on brand essence through visual metaphor
"""
    
    negative_prompt = "UI elements, browser interface, website screenshot, messy layout, cluttered, blurry, low quality, watermark, signature, small unreadable text, random Korean text, chaotic composition"
    
    # Use new HF router endpoint directly
    headers = {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 28,  # Higher steps for better quality
            "guidance_scale": 3.5,  # Optimal balance for detail and prompt adherence
            "width": 768,   # 9:16 ratio width
            "height": 1344, # 9:16 ratio height (optimal for Flux Dev)
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Use new HF Router endpoint
        response = await client.post(
            f"https://router.huggingface.co/hf-inference/models/{settings.flux_model}",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        image_bytes = response.content
    
    # Save generated image
    poster_path = '/tmp/poster.png'
    img = Image.open(io.BytesIO(image_bytes))
    img.save(poster_path)
    
    return poster_path
