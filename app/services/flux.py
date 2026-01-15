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
    title = analysis.get('title', 'Brand')
    atmosphere = analysis.get('atmosphere', 'modern and clean aesthetic')
    primary_color = analysis.get('primary_color', '#000000')
    accent_color = analysis.get('accent_color', '#FFFFFF')
    keywords = ', '.join(analysis.get('keywords', ['modern', 'minimal']))
    
    prompt = f"""
A high-fashion square poster design (1:1 ratio). 

VISUAL CONCEPT:
- Brand essence: {title}
- Atmosphere: {atmosphere}
- Abstract metaphor representing the service (NOT website UI)
- NO buttons, NO browser elements, NO screenshots

TEXT INTEGRATION:
- Render "{title}" as a physical 3D object in the scene
- Style options: Neon sign, Gold engraving, Concrete letters, Holographic floating text
- Position: Center or top-center, bold typography
- ENGLISH ONLY (no Korean characters)

COLOR PALETTE:
- Primary: {primary_color}
- Accent: {accent_color}
- Professional gradient or solid backgrounds

STYLE & QUALITY:
- Abstract, geometric, minimalist luxury branding
- Keywords: {keywords}
- Unreal Engine 5 render, 8K, volumetric lighting
- Cinematic composition, award-winning design
- Professional graphic design aesthetic
"""
    negative_prompt = "text, letters, words, typography, watermark, signature, blurry, low quality, photograph, realistic, 3d render"
    
    # Use new HF router endpoint directly
    headers = {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": settings.flux_steps,
            "guidance_scale": 0.0,
            "width": 1024,
            "height": 1024,
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
