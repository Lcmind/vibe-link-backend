"""Gemini AI analysis service."""

import google.generativeai as genai
from PIL import Image
import json
from app.core.config import settings


# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


async def analyze_with_gemini(screenshot_path: str, extracted_text: str = "") -> dict:
    """
    Analyze website screenshot using Gemini Vision AI.
    
    Args:
        screenshot_path: Path to the screenshot file
        extracted_text: DOM text extracted from the website
        
    Returns:
        dict: Analysis results with title, atmosphere, colors, and keywords
        
    Raises:
        Exception: If analysis fails
    """
    model = genai.GenerativeModel(settings.gemini_model)
    img = Image.open(screenshot_path)
    
    # DOM 텍스트를 프롬프트에 추가
    context_text = f"\n\n=== WEBSITE TEXT CONTEXT ===\n{extracted_text[:2000]}\n" if extracted_text else ""
    
    prompt = f"""
You are a Senior Creative Director analyzing a website screenshot for a commercial poster design.

=== TASK ===
Extract key information to create a poster that VISUALLY REPRESENTS what this company does.

=== ANALYSIS STEPS ===

1. **WHAT IS THIS?** (Read the screen carefully)
   - Company/Brand name (if Korean, romanize: 무신사→MUSINSA)
   - What do they sell or provide? Be SPECIFIC.
   - Who is the target user?

2. **VISUAL TRANSLATION** (Convert business to imagery)
   
   The poster must show OBJECTS that represent the business:
   
   | Business Type | What to Show |
   |--------------|--------------|
   | Productivity Tool | Organized workspace, floating UI panels, clean desk, glass screens with icons |
   | Fashion Store | Clothes on racks, sneakers, fashion photography studio |
   | Search/Tech | Holographic interfaces, data streams, futuristic screens |
   | Delivery | Flying boxes, warehouse, conveyor belts |
   | Food | The food items, kitchen, restaurant interior |
   
3. **COLOR EXTRACTION**
   - What is the main brand color from the logo/design?
   - Is it single color or multi-color brand?

=== OUTPUT (JSON) ===
{
  "brand_name": "ENGLISH brand name",
  "business_type": "Productivity/Fashion/Tech/Delivery/Food/Other",
  "what_they_provide": "Specific description in 15 words",
  "poster_objects": "List concrete objects: 'glass panels, folder icon, chat icon, checklist, modern desk, soft lighting'",
  "background_style": "Clean gradient/Studio/Futuristic/Warehouse/Minimal",
  "primary_color": "#hexcode",
  "mood": "Clean/Premium/Energetic/Calm"
}
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
