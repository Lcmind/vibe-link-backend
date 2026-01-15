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
You are a **Commercial Poster Art Director**.
Analyze this website screenshot and design a visual concept for a brand poster.

=== STEP 1: READ THE WEBSITE (MANDATORY) ===

1. **What text do you see?**
   - Headlines, menu items, buttons, taglines
   
2. **What is this website FOR?** (Be SPECIFIC)
   - ❌ WRONG: "It's a tech company"
   - ✅ RIGHT: "Team collaboration tool with chat, file sharing, task management, and scheduling"

3. **Brand name?** (Romanize Korean: 무신사→MUSINSA, 포커스허브→FOCUSHUB)

4. **Main color?** (Extract the dominant color from the logo/design)

=== STEP 2: DESIGN THE POSTER SCENE ===

**CRITICAL RULE**: The poster must VISUALLY REPRESENT what the company DOES.

**Examples of CORRECT visual translation:**

📁 **Productivity Tool (FocusHub, Notion, Slack):**
- SHOW: Floating glass panels with app icons (folder, chat bubble, checklist, calendar)
- SHOW: Clean desk setup with organized digital screens
- SHOW: Minimalist workspace with transparent UI elements
- COLOR: Blue/white/gray tones (professional, clean)
- MOOD: Organized, calm, productive

👕 **Fashion E-commerce (Musinsa, Zara):**
- SHOW: Clothing items spread on floor or hanging on racks
- SHOW: Sneakers, hoodies, jackets arranged artistically
- SHOW: Fashion photography studio setup
- COLOR: Black/white with accent colors
- MOOD: Trendy, stylish, premium

🔍 **Search Engine / Tech (Google, Naver):**
- SHOW: Holographic search interfaces, data visualization
- SHOW: Flowing data streams, connected nodes
- SHOW: Futuristic command center with screens
- COLOR: Brand's signature colors (Google: blue/red/yellow/green)
- MOOD: Intelligent, connected, powerful

📦 **Delivery / Logistics (Coupang, Amazon):**
- SHOW: Flying boxes with motion blur
- SHOW: Futuristic warehouse conveyor systems
- SHOW: Speed lines, delivery trucks, packages
- COLOR: Brand colors with dynamic lighting
- MOOD: Fast, efficient, massive scale

=== STEP 3: OUTPUT ===

Think carefully about what the website actually PROVIDES, then describe a scene that SHOWS it.

{
  "brand_name": "ENGLISH name (romanized if Korean)",
  "what_they_do": "Specific description of their service/product (20 words)",
  "poster_scene": "CONCRETE description of objects in the poster (40+ words). List actual objects: 'floating glass panels showing folder icon, chat bubble icon, checklist icon, calendar icon, arranged in a 2x2 grid, deep blue gradient background, soft white glow'",
  "color_palette": {
    "primary": "#hexcode",
    "secondary": ["#hex1", "#hex2"]
  },
  "mood": "2-3 word mood description",
  "objects_list": ["object1", "object2", "object3", "object4"]
}

**JSON ONLY. No other text.**
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
