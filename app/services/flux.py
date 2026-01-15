"""Flux AI image generation service."""

import httpx
from PIL import Image
import io
from app.core.config import settings


async def generate_poster(analysis: dict) -> str:
    """
    Generate a poster using Flux.1-schnell based on analysis.
    Flux generates the brand name text directly in the image.
    
    Args:
        analysis: Analysis results from Gemini
        
    Returns:
        str: Path to the generated poster image
        
    Raises:
        Exception: If generation fails
    """
    # Extract analysis data
    brand_name = analysis.get('brand_name', 'BRAND').upper()
    business_type = analysis.get('business_type', 'Productivity')
    poster_objects = analysis.get('poster_objects', 'modern workspace elements')
    background_style = analysis.get('background_style', 'Clean gradient')
    primary_color = analysis.get('primary_color', '#4A90D9')
    mood = analysis.get('mood', 'Clean')
    
    # === PROMPT MASTER'S TEXT GENERATION RULES FOR FLUX ===
    # 
    # Rule 1: Quote the text exactly - Flux reads quoted strings
    # Rule 2: Specify font style and weight (bold, sans-serif, etc.)
    # Rule 3: Specify exact position (top center, bottom left, etc.)
    # Rule 4: Make text part of the design context (signage, neon, embossed)
    # Rule 5: Keep text SHORT (1-2 words max for reliability)
    
    prompt = f"""High-end commercial poster design, vertical 9:16 format.

Typography: Bold modern text "{brand_name}" prominently displayed at top center of the frame, clean sans-serif font, white text with subtle shadow, professional branding typography.

Scene: {poster_objects} arranged beautifully below the text, {background_style} setting, {mood.lower()} atmosphere.

Color palette: {primary_color} as accent color, harmonious tones throughout.

Style: Premium advertising campaign aesthetic, Apple-style minimalism, magazine cover quality, professional product photography.

Technical: Studio lighting, soft shadows, sharp focus, 8k resolution, commercial photography, masterpiece."""
    
    # Negative prompt - allow text but block unwanted elements
    negative_prompt = "blurry, noise, grainy, amateur, low quality, distorted, ugly, planets, space, galaxy, stars, cosmos, abstract art, random patterns, cluttered, messy, chaotic, bad typography, misspelled text, distorted letters, unreadable text"
    
    headers = {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": "application/json"
    }
    
    # Flux.1-schnell optimal parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 4,  # Schnell is optimized for 4 steps
            "guidance_scale": 0.0,     # Schnell uses guidance_scale 0
            "width": 768,
            "height": 1344,
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
