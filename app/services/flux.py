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
    what_they_do = analysis.get('what_they_do', 'innovative service')
    visual_scene = analysis.get('visual_scene', 'modern clean environment')
    color_palette = analysis.get('color_palette', {'primary': '#000000', 'secondary': []})
    mood = analysis.get('mood', 'professional modern')
    key_objects = analysis.get('key_objects', ['modern design'])
    
    primary_color = color_palette.get('primary', '#000000')
    secondary_colors = color_palette.get('secondary', [])
    
    # Build color lighting description
    if secondary_colors and len(secondary_colors) > 1:
        colors_list = [primary_color] + secondary_colors
        color_lighting = f"Multi-colored lighting and accents in {', '.join(colors_list)}"
    else:
        color_lighting = f"Dramatic {primary_color} colored lighting and accents"
    
    # Key objects for scene
    objects_desc = ', '.join(key_objects) if key_objects else 'modern elements'
    
    prompt = f"""
A stunning vertical commercial poster (9:16 aspect ratio, 768x1344px).

THE SCENE (WHAT THIS BRAND REPRESENTS):
{visual_scene}

KEY VISUAL ELEMENTS IN THE SCENE:
- {objects_desc}
- A large prominent display area or glowing sign placeholder in the center-top
- The scene should clearly communicate: {what_they_do}

LIGHTING & COLOR ATMOSPHERE:
- {color_lighting}
- Mood: {mood}
- Cinematic volumetric lighting with dramatic depth

COMPOSITION:
- Clean, organized layout
- Negative space around the center-top for branding area
- Everything leads the eye to the center focal point

TECHNICAL QUALITY:
- Ultra-detailed commercial photography
- 8K resolution, Unreal Engine 5 quality
- Octane Render, Ray Tracing
- Professional advertising poster aesthetic
- Sharp focus, perfect exposure

STYLE:
- High-end brand commercial
- Magazine cover quality
- Premium advertising campaign aesthetic
"""
    
    negative_prompt = "text, words, letters, typography, watermark, logo, brand name, signature, blurry, low quality, amateur, messy, cluttered, chaotic, random patterns, liquid metal, abstract noise, distorted, warped, ugly, deformed"
    
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
