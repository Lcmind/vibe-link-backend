"""Gemini AI analysis service."""

import google.generativeai as genai
from PIL import Image
import json
from app.core.config import settings


# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


async def analyze_with_gemini(screenshot_path: str) -> dict:
    """
    Analyze website screenshot using Gemini Vision AI.
    
    Args:
        screenshot_path: Path to the screenshot file
        
    Returns:
        dict: Analysis results with title, atmosphere, colors, and keywords
        
    Raises:
        Exception: If analysis fails
    """
    model = genai.GenerativeModel(settings.gemini_model)
    img = Image.open(screenshot_path)
    
    prompt = """
You are a **Legendary Marketing CEO & Creative Director**.
Your mission is to translate a website screenshot into a **High-End Commercial Brand Poster** that captures the absolute "Essence" of the business.

*** PHASE 1: BUSINESS INTELLIGENCE (The CEO's Insight) ***
Read the text, UI, and context to determine the **Business Model**.

1. **IDENTIFY THE CATEGORY & METAPHOR:**
   - **Fashion/Commerce (e.g., Musinsa, Chanel):** - *Essence:* Style, Trend, Elegance.
     - *Visual Metaphor:* Infinite runway, floating silk fabrics, high-end showroom, mannequins.
   - **Logistics/Delivery (e.g., Coupang, FedEx):** - *Essence:* Speed, Motion, Scale.
     - *Visual Metaphor:* Motion blur lines, flying boxes, futuristic warehouse tunnel, fast trucks.
   - **Tech/AI/Search (e.g., Google, Naver):** - *Essence:* Intelligence, Data, Connection.
     - *Visual Metaphor:* Digital brain, glowing neural nodes, fiber optic cables, infinite library of light.
   - **Productivity/SaaS (e.g., FocusHub, Notion):** - *Essence:* Clarity, Order, Flow.
     - *Visual Metaphor:* Perfect geometric glass cubes, zen garden, assembling structures, clean water surface.
   - **Luxury/Perfume:** - *Essence:* Scent, Nature, Premium.
     - *Visual Metaphor:* Marble stone, flowers, gold accents, water ripples, soft sunlight.

2. **EXTRACT BRAND IDENTITY (CRITICAL):**
   - **Brand Name:** Find the logo. **MANDATORY:** If Korean, Romanize/Translate to English (e.g., '무신사' -> 'MUSINSA').
   - **Brand Color:** Identify the dominant color to set the lighting mood.

*** PHASE 2: VISUAL STRATEGY (The Director's Vision) ***
- **Rule 1: TEXT IS HERO.** The Brand Name is not just a caption. It is the **Main 3D Art Piece** in the center.
- **Rule 2: MATERIALITY.** Define what the text is made of (Neon, Gold, Concrete, Cloud, Metal) based on the category.

*** OUTPUT FORMAT (JSON ONLY) ***
{
  "title": "Brand name in ENGLISH (romanized if Korean)",
  "category": "One of: Fashion, Logistics, Tech, Productivity, Luxury, Creative",
  "business_essence": "Core value in 3-5 words (e.g., 'Speed, Motion, Scale')",
  "visual_metaphor": "Concrete scene description (e.g., 'flying boxes and motion blur lines')",
  "text_material": "Material for brand text (e.g., 'glowing neon tubes', 'gold engraving', 'concrete letters')",
  "primary_color": "Main color hex code (from website)",
  "accent_color": "Accent color hex code",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}

**Output JSON ONLY. No extra text.**
"""
    
    response = model.generate_content([prompt, img])
    
    # Parse JSON from response with multiple fallback strategies
    text = response.text.strip()
    
    # Try to extract JSON from markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    # Remove any leading/trailing non-JSON characters
    text = text[text.find('{'):text.rfind('}')+1]
    
    try:
        analysis = json.loads(text)
        return analysis
    except json.JSONDecodeError as e:
        # If JSON parsing fails, try to fix common issues
        text = text.replace("'", '"').replace('\n', ' ')
        try:
            analysis = json.loads(text)
            return analysis
        except:
            raise Exception(f"Failed to parse Gemini response as JSON: {text[:200]}")
