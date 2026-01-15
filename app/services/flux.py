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
    category = analysis.get('category', 'Productivity')
    hero_object = analysis.get('hero_object', 'a floating glass cube')
    atmosphere = analysis.get('atmosphere', 'modern and clean aesthetic')
    primary_color = analysis.get('primary_color', '#000000')
    accent_color = analysis.get('accent_color', '#FFFFFF')
    keywords = ', '.join(analysis.get('keywords', ['modern', 'minimal']))
    
    # Category-specific style rules
    if category == 'Productivity':
        style_keywords = "Apple Style, Dieter Rams, Frosted Glass, Soft Studio Lighting, Minimalist, Zen, Spacious, Air"
        negative_additions = "NO cluttered elements, NO complex machinery, NO glitch effects, NO random messy lines"
    elif category == 'Dev':
        style_keywords = "Matrix style, Clean dark mode, Terminal aesthetic, Code-inspired"
        negative_additions = ""
    elif category == 'Creative':
        style_keywords = "Colorful, Abstract, Artistic, Expressive"
        negative_additions = ""
    else:
        style_keywords = "Modern, Professional, Clean"
        negative_additions = ""
    
    prompt = f"""
A high-end vertical commercial poster design (9:16 aspect ratio, 768x1344px).

COMPOSITION (MANDATORY):
- **Center Composition:** Place '{hero_object}' in the center
- **Negative Space:** Leave 40% of the image empty (clean background) to symbolize calmness
- **Hero Object:** {hero_object}

BRAND TEXT:
- The word '{title}' formed by a 3D object (glowing neon tube floating in air, or engraved in metal)
- Font style: Swiss Typography, Clean Sans-serif
- Position: Top-center or integrated with hero object
- ENGLISH ONLY (no Korean characters)

COLOR PALETTE (STRICT):
- Primary: {primary_color}
- Accent: {accent_color}
- Use gradients or solid backgrounds only

STYLE ENFORCERS:
- {style_keywords}
- Keywords: {keywords}
- Atmosphere: {atmosphere}

QUALITY BOOSTERS:
- Unreal Engine 5, 8K, Octane Render, Ray Tracing
- Super-Resolution, Anti-Aliasing
- Cinematic composition, award-winning design

CATEGORY: {category}
"""
    
    negative_prompt = f"text, letters, words, typography, watermark, signature, blurry, low quality, photograph, realistic, 3d render, {negative_additions}"
    
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
