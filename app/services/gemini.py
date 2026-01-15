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
You are a **World-Class Brand Strategist & Visual Translator**.
Your mission: Analyze the website screenshot and create a SPECIFIC visual concept for a commercial poster.

*** CRITICAL INSTRUCTIONS ***

**PHASE 1: DEEP BUSINESS ANALYSIS (What do they actually DO?)**

1. **READ THE SCREEN (OCR is MANDATORY):**
   - What is the MAIN headline/tagline?
   - What buttons/menus do you see? (e.g., "Shop Now", "Search", "Sign In", "Upload File", "Team Chat")
   - What images/icons are visible? (clothes, search bar, charts, food, etc.)

2. **DETERMINE THE CORE OFFERING (BE SPECIFIC):**
   - **BAD (Too Generic):** "It's a tech company."
   - **GOOD (Precise):** "It's a cloud storage service for file sharing" OR "It's a fashion e-commerce selling streetwear."
   
   Examples:
   - **Musinsa (무신사):** "Fashion e-commerce platform selling Korean streetwear and sneakers."
   - **Google:** "Global search engine with AI, cloud services, and productivity tools."
   - **FocusHub:** "Team productivity hub with file library, team chat, agenda, and task management."
   - **Coupang:** "Fast delivery e-commerce with rocket shipping."

3. **EXTRACT VISUAL SIGNATURE:**
   - **Brand Name:** (Korean -> Romanize. e.g., '무신사' -> 'MUSINSA')
   - **Logo Color Palette:** What are the EXACT colors? (Single color like #4285F4 Blue, or Multi-color like Google's Blue/Red/Yellow/Green)

--------------------------------------------------------------------------------

**PHASE 2: VISUAL METAPHOR CREATION (Turn offering into IMAGE)**

Based on what you found, define the CONCRETE VISUAL ELEMENTS for the poster.

**Rules:**
- **DO NOT use generic templates** (e.g., "abstract tech background").
- **BE HYPER-SPECIFIC** to what the brand sells/provides.

**Examples:**

* **Musinsa (Fashion E-Commerce):**
  - Visual: "Hundreds of trendy clothing items (hoodies, sneakers, jackets) arranged in a grid pattern on a clean white studio floor, with soft spotlights from above."
  - Brand Text Material: "The word 'MUSINSA' in bold black modern sans-serif, standing upright as a physical 3D sign on the floor."

* **Google (Search/AI/Cloud):**
  - Visual: "A vast digital universe with flowing streams of colorful light (blue, red, yellow, green) representing search queries and data, converging into a glowing search bar in the center."
  - Brand Text Material: "The word 'Google' in its signature multi-colored letters (Blue G, Red o, Yellow o, Blue g, Green l, Red e), rendered as glowing 3D neon tubes floating in space."

* **FocusHub (Productivity Tool):**
  - Visual: "A clean organized digital workspace with floating transparent glass panels showing icons of: file folder, chat bubble, checklist, calendar. Everything is aligned in perfect symmetry with a deep blue gradient background."
  - Brand Text Material: "The word 'FOCUSHUB' in glowing blue neon letters, positioned center-top."

* **Coupang (Fast Delivery):**
  - Visual: "Hundreds of cardboard boxes flying through a futuristic tunnel with motion blur trails, representing hyper-speed logistics."
  - Brand Text Material: "The word 'COUPANG' in bold white letters on the side of a large delivery box."

--------------------------------------------------------------------------------

*** OUTPUT FORMAT (JSON ONLY) ***
{
  "brand_name": "Brand name in ENGLISH (romanized if Korean)",
  "core_offering": "Specific description of what they provide (20 words max)",
  "visual_scene": "Detailed description of the poster's background environment (40 words, be CONCRETE)",
  "brand_text_material": "How the brand name appears as a 3D object (e.g., 'glowing blue neon', 'black modern signage', 'multi-colored glass letters')",
  "primary_color": "Main brand color hex code",
  "secondary_colors": "Array of additional brand colors if multi-color logo (e.g., ['#4285F4', '#EA4335', '#FBBC04', '#34A853'] for Google), or empty [] if single color",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}

**Output JSON ONLY. No explanations.**
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
