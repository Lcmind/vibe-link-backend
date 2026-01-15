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
You are a **Minimalist Brand Director** (think Apple or Dieter Rams style).
Your mission is to analyze the website screenshot and extract its "Visual Soul" for a high-end poster.

*** CRITICAL ANALYSIS PROTOCOL ***

1. **READ THE TEXT & CONTEXT (OCR):**
   - Look for keywords: "Focus", "Task", "Simple", "Flow", "Team".
   - **JUDGMENT:**
     - If it's a **Productivity/Tool** (like FocusHub): The visual MUST be **Clean, Organized, Zen, Glass-like**. (FORBIDDEN: Chaos, messy wires, glitch art).
     - If it's **Creative/Art**: Colorful and abstract is okay.
     - If it's **Dev/Code**: Matrix style or clean dark mode is okay.

2. **VISUAL ANCHOR (The Main Subject):**
   - Don't just say "abstract background". Define a **Single "Hero Object"**.
   - *Good Examples:* "A single perfect crystal cube", "A glowing ring of light", "A floating glass sheet".
   - *Bad Examples:* "Complex city", "Random shapes", "Circuit board patterns".

3. **BRAND IDENTITY:**
   - **Name:** If Korean detected, Romanize it (e.g., '집중' -> 'FOCUS').
   - **Color:** Strict adherence to the site's dominant color (e.g., Deep Blue -> keep it Blue/Indigo, don't add random Pink/Purple).

*** OUTPUT FORMAT (JSON ONLY) ***
{
  "title": "Core brand keyword in 1-2 words (ENGLISH ONLY)",
  "category": "One of: Productivity, Creative, Dev, Commerce, Social",
  "hero_object": "Single concrete visual element for the poster (e.g., 'floating glass cube')",
  "atmosphere": "Visual mood description in 20 words (ENGLISH)",
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
