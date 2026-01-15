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
    title = analysis.get('title', 'BRAND')
    category = analysis.get('category', 'Tech')
    business_essence = analysis.get('business_essence', 'modern and innovative')
    visual_metaphor = analysis.get('visual_metaphor', 'abstract geometric shapes')
    text_material = analysis.get('text_material', 'glowing neon tubes')
    primary_color = analysis.get('primary_color', '#000000')
    accent_color = analysis.get('accent_color', '#FFFFFF')
    keywords = ', '.join(analysis.get('keywords', ['modern', 'minimal']))
    
    prompt = f"""
A high-end vertical commercial poster (9:16 aspect ratio, 768x1344px). 

THE HERO SUBJECT (TEXT MASTERY):
The text '{title}' is the main masterpiece of the image.
The text '{title}' is made of {text_material}.
Typography-centric design, Big Bold Legible Text, positioned in the center or top-center.

THE CINEMATIC ENVIRONMENT (BUSINESS METAPHOR):
Category: {category}
Business essence: {business_essence}
Surrounded by: {visual_metaphor}

LIGHTING & COLOR:
- Primary color mood: {primary_color}
- Accent highlights: {accent_color}
- Cinematic lighting, dramatic atmosphere
- Professional commercial photography style

STYLE & QUALITY:
- Keywords: {keywords}
- 8K resolution, Unreal Engine 5, Octane Render
- Award-winning commercial poster design
- Clean composition, no UI elements, no browser bars

ENGLISH TEXT ONLY (no Korean characters).
"""
    
    negative_prompt = "messy UI elements, browser bars, glitch errors, blurry, low quality, watermark, signature, cluttered, chaotic, random text, small text, unreadable text"
    
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
