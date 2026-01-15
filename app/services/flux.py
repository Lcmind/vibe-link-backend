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
    what_they_do = analysis.get('what_they_do', 'service')
    poster_scene = analysis.get('poster_scene', 'modern clean design')
    color_palette = analysis.get('color_palette', {'primary': '#4A90D9', 'secondary': []})
    mood = analysis.get('mood', 'professional')
    objects_list = analysis.get('objects_list', ['modern design elements'])
    
    primary_color = color_palette.get('primary', '#4A90D9')
    secondary_colors = color_palette.get('secondary', [])
    
    # Build specific color instruction
    if secondary_colors and len(secondary_colors) > 1:
        all_colors = [primary_color] + secondary_colors
        color_instruction = f"Color scheme using {', '.join(all_colors)} as accent colors throughout the scene"
    else:
        color_instruction = f"Color scheme dominated by {primary_color} with white and dark accents"
    
    # Build objects description
    objects_desc = ', '.join(objects_list) if objects_list else 'clean design elements'
    
    prompt = f"""
Commercial brand poster, vertical 9:16 aspect ratio.

SCENE DESCRIPTION:
{poster_scene}

KEY OBJECTS TO INCLUDE:
{objects_desc}

COLOR AND LIGHTING:
{color_instruction}
{mood} atmosphere
Professional studio lighting, soft shadows, cinematic depth

STYLE REQUIREMENTS:
- Clean, modern, minimalist composition
- Professional advertising photography quality
- High-end brand commercial aesthetic
- NO text, NO words, NO letters in the image
- Leave empty space at top center for logo placement

TECHNICAL:
- 8K resolution quality
- Sharp focus throughout
- Professional color grading
- Magazine advertisement quality
"""
    
    negative_prompt = "text, words, letters, numbers, typography, watermark, signature, logo, brand name, writing, caption, label, blurry, low quality, amateur, messy, cluttered, chaotic, ugly, distorted, deformed, oversaturated, planets, space, galaxy, cosmos, moons, stars, universe"
    
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
