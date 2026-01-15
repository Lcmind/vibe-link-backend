"""Flux AI image generation service."""

from huggingface_hub import InferenceClient
from PIL import Image
import io
from app.core.config import settings


# Initialize Hugging Face Inference Client with new router endpoint
hf_client = InferenceClient(
    token=settings.hf_token,
    base_url="https://router.huggingface.co"
)


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
Professional brand poster design for "{title}".
Atmosphere: {atmosphere}
Style: Abstract, geometric, minimalist, high-end branding
Color palette: {primary_color} and {accent_color}
Elements: {keywords}
Composition: Centered, balanced, luxury brand aesthetic
Quality: 8K, ultra-detailed, professional graphic design, award-winning
"""
    
    negative_prompt = "text, letters, words, typography, watermark, signature, blurry, low quality, photograph, realistic, 3d render"
    
    # Generate image using Flux.1-schnell (4 steps, fast)
    image_bytes = hf_client.text_to_image(
        prompt=prompt,
        negative_prompt=negative_prompt,
        model=settings.flux_model,
        num_inference_steps=settings.flux_steps,
        guidance_scale=0.0,  # Schnell doesn't use guidance scale
        width=1024,
        height=1024,
    )
    
    # Save generated image
    poster_path = '/tmp/poster.png'
    
    # Convert bytes to PIL Image and save
    if isinstance(image_bytes, bytes):
        img = Image.open(io.BytesIO(image_bytes))
    else:
        img = image_bytes
    
    img.save(poster_path)
    
    return poster_path
