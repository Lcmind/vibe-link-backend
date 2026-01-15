"""Flux AI image generation service."""

import httpx
from PIL import Image
import io
from app.core.config import settings


async def generate_poster(analysis: dict) -> str:
    """
    Generate a poster using Flux.1-schnell based on analysis.
    
    Args:
        analysis: Analysis results from Gemini
        
    Returns:
        str: Path to the generated poster image
        
    Raises:
        Exception: If generation fails
    """
    # Extract analysis data with new schema
    business_type = analysis.get('business_type', 'Productivity')
    poster_objects = analysis.get('poster_objects', 'modern workspace elements')
    background_style = analysis.get('background_style', 'Clean gradient')
    primary_color = analysis.get('primary_color', '#4A90D9')
    mood = analysis.get('mood', 'Clean')
    
    # === 10-YEAR PROMPT ENGINEER'S PERFECT PROMPT STRUCTURE ===
    # 
    # Rule 1: Start with medium and format
    # Rule 2: Subject first, then style
    # Rule 3: Be concrete, not abstract
    # Rule 4: Quality tags at the end
    # Rule 5: Negative prompt blocks unwanted elements
    
    prompt = f"""Commercial photography poster, vertical composition, 9:16 aspect ratio.

Subject: {poster_objects}, arranged aesthetically in frame.

Environment: {background_style} background, professional studio setup, {mood.lower()} atmosphere.

Lighting: Soft diffused studio lighting, subtle shadows, {primary_color} color accents in the scene.

Style: High-end advertising campaign, clean minimalist design, modern corporate aesthetic, magazine quality.

Composition: Empty space at top 15% of frame for text overlay, centered focal point, balanced layout.

Quality: 8k resolution, sharp focus, professional color grading, commercial photography."""
    
    # Optimized negative prompt - specific and targeted
    negative_prompt = "text, words, letters, typography, watermark, logo, signature, blurry, noise, grainy, amateur, low quality, distorted, ugly, planets, space, galaxy, stars, cosmos, abstract art, random patterns, cluttered, messy, chaotic"
    
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
