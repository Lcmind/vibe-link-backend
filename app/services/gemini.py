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
You are an **Elite Visual UX Researcher & Brand Strategist**.
Your mission is to perform a "Deep Contextual Analysis" of the provided website screenshot.

*** CORE TASK: READ THE SOUL OF THE SERVICE ***
Do not just look at the colors. You must **READ the text (OCR)** and **INTERPRET the purpose**.

1. **OCR & Context Extraction (MANDATORY):**
   - Read the Headline (H1), Sub-headline, and Buttons.
   - **Answer this:** What problem does this service solve?
     - *Example:* If text says "Track your time", the essence is **"EFFICIENCY & FLOW"**.
     - *Example:* If text says "Premium Leather", the essence is **"CRAFTSMANSHIP & LUXURY"**.
     - *Example:* If text says "Shin Ramyun", the essence is **"SPICY & ENERGY"**.

2. **Target Audience Profiling:**
   - Who uses this? (Gamers? CEOs? Parents? Developers?)
   - The final visual must appeal to their specific taste.

3. **Brand Identity Decoding:**
   - **Name:** Find the logo or brand name.
     - **RULE:** If Korean (Hangul) is detected, **Translate/Romanize it to English** immediately. (e.g., '집중' -> 'FOCUS').
   - **Color Psychology:** What mood do the colors convey? (Trust, Passion, Calm).

*** OUTPUT FORMAT (JSON ONLY) ***
{
  "title": "Core brand keyword in 1-2 words (ENGLISH ONLY)",
  "atmosphere": "Visual mood description in 30 words (ENGLISH)",
  "primary_color": "Main color hex code",
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
