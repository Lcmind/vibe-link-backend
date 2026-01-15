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
You are a **World-Class Brand Visualizer & Marketing Strategist**.
Your mission: Analyze the website screenshot and create a POWERFUL visual concept that captures the brand's CORE IDENTITY.

*** CRITICAL: WHAT DO YOU SEE? ***

**PHASE 1: OCR & BUSINESS ANALYSIS**
1. **Read Everything on Screen:**
   - Main headline/tagline
   - Menu items, buttons
   - What images/products are shown?

2. **Determine the EXACT Business:**
   - What do they SELL or PROVIDE?
   - Who is the TARGET USER?
   
   **BE HYPER-SPECIFIC:**
   - ❌ BAD: "Tech company" 
   - ✅ GOOD: "Search engine with AI assistant, email, cloud storage, maps"
   
   - ❌ BAD: "Fashion store"
   - ✅ GOOD: "Korean streetwear e-commerce selling hoodies, sneakers, and accessories"

**PHASE 2: BRAND VISUAL IDENTITY**
1. **Brand Name:** (If Korean, romanize: '무신사' -> 'MUSINSA')
2. **Logo Colors:** 
   - Is it MULTI-COLOR? (like Google: Blue, Red, Yellow, Green) 
   - Or SINGLE COLOR? (like Facebook Blue, Naver Green)

**PHASE 3: VISUAL SCENE DESIGN**

Design a scene that SHOWS what they do WITHOUT relying on text.

**Examples of GOOD Visual Scenes:**

* **Google (Search/AI):**
  - "A futuristic command center with floating holographic search interfaces, glowing blue/red/yellow/green data streams flowing through the air, massive holographic screens showing search results, maps, emails, and AI chat bubbles. Clean white and chrome environment."

* **Musinsa (Fashion E-commerce):**
  - "A massive high-fashion warehouse with thousands of trendy clothes (hoodies, sneakers, jackets) organized on sleek white shelves, dramatic overhead spotlights, clean concrete floor reflecting the lights. A giant glowing sign in the background."

* **FocusHub (Productivity Tool):**
  - "A pristine digital workspace floating in deep blue space. Transparent glass panels displaying: a file folder icon, a chat bubble icon, a checklist icon, a calendar icon. Everything perfectly aligned in symmetry with soft blue glow."

* **Coupang (Fast Delivery):**
  - "A hyper-speed logistics tunnel with thousands of cardboard boxes flying past in motion blur. Neon light trails. Futuristic conveyor belts. Speed lines everywhere."

**PHASE 4: TEXT STRATEGY (CRITICAL)**

Since AI image generators struggle with text, describe where a sign/logo WOULD be placed:
- "A large glowing sign area in the center-top of the image"
- "A prominent display board in the scene"

--------------------------------------------------------------------------------

*** OUTPUT FORMAT (JSON ONLY) ***
{
  "brand_name": "ENGLISH brand name (romanized if Korean)",
  "what_they_do": "Specific description: what they sell/provide + target users (25 words max)",
  "visual_scene": "DETAILED description of the scene that represents their business (50+ words, be CONCRETE with objects, colors, lighting)",
  "color_palette": {
    "primary": "#hex",
    "secondary": ["#hex1", "#hex2"] 
  },
  "mood": "The emotional feel (e.g., 'High-tech futuristic', 'Premium fashion', 'Clean productive')",
  "key_objects": ["object1", "object2", "object3", "object4", "object5"]
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
