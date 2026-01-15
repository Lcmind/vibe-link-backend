"""Flux AI image generation service."""

import httpx
from PIL import Image
import io
from app.core.config import settings


def hex_to_color_name(hex_color: str) -> str:
    """Convert hex color to descriptive color name to prevent hex appearing in image."""
    hex_color = hex_color.upper().replace('#', '')
    
    # Common brand colors mapping
    color_map = {
        '4285F4': 'vibrant blue',      # Google Blue
        'DB4437': 'warm red',           # Google Red
        'F4B400': 'golden yellow',      # Google Yellow
        '0F9D58': 'fresh green',        # Google Green
        '1877F2': 'facebook blue',
        'FF0000': 'bold red',           # YouTube
        '000000': 'deep black',
        'FFFFFF': 'pure white',
        '4A90D9': 'sky blue',
        'FF6B6B': 'coral pink',
        '6C5CE7': 'electric purple',
        '00D4AA': 'mint green',
        'FFD93D': 'sunny yellow',
    }
    
    if hex_color in color_map:
        return color_map[hex_color]
    
    # Parse RGB and describe
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Determine dominant color
        if r > g and r > b:
            if r > 200: return 'bright red tones'
            return 'warm red tones'
        elif g > r and g > b:
            if g > 200: return 'vibrant green tones'
            return 'fresh green tones'
        elif b > r and b > g:
            if b > 200: return 'bright blue tones'
            return 'cool blue tones'
        elif r > 200 and g > 200:
            return 'warm golden tones'
        elif r > 200 and b > 200:
            return 'magenta pink tones'
        elif g > 200 and b > 200:
            return 'cyan aqua tones'
        else:
            return 'neutral tones'
    except:
        return 'harmonious tones'


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
    poster_objects = analysis.get('poster_objects', 'modern workspace elements')
    background_style = analysis.get('background_style', 'Clean gradient')
    primary_color = analysis.get('primary_color', '#4A90D9')
    mood = analysis.get('mood', 'Clean')
    
    # Convert hex to color name (prevents hex code appearing in image)
    color_description = hex_to_color_name(primary_color)
    
    # === S-TIER PROMPT ENGINEER RULES ===
    # 
    # Rule 1: ONLY the brand name as readable text
    # Rule 2: All other UI elements = blurred/abstract/no text
    # Rule 3: Color as description, NOT hex code
    # Rule 4: Explicit "no watermark" in both prompt and negative
    # Rule 5: Clean, minimal composition
    
    prompt = f"""Minimalist commercial poster, vertical 9:16 aspect ratio, ultra clean design.

The word "{brand_name}" in bold white sans-serif typography, centered at top, professional lettering with soft drop shadow.

Below: {poster_objects} with all screens and interfaces showing abstract colorful shapes and blurred gradients instead of text, no readable text on any UI element, purely visual design elements.

Background: {background_style}, {mood.lower()} mood, {color_description} color scheme.

Style: Apple keynote presentation quality, premium advertising, high-end product showcase, pristine studio photography, no watermarks, no signatures, no logos except the brand name."""
    
    # Aggressive negative prompt for clean output
    negative_prompt = "watermark, signature, logo, copyright, trademark, website url, username, id number, serial number, code, hex code, random letters, gibberish text, corrupted text, glitched text, small text, fine print, label, tag, badge, stamp, readable text on screens, text on monitors, text on UI, multiple texts, extra text, any text except brand name"
    
    headers = {
        "Authorization": f"Bearer {settings.hf_token}",
        "Content-Type": "application/json"
    }
    
    # Flux.1-schnell optimal parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 4,
            "guidance_scale": 0.0,
            "width": 768,
            "height": 1344,
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
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
