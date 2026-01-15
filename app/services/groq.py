"""Groq Llama-4-Maverick 멀티모달 분석 서비스."""

import httpx
from PIL import Image
import base64
import json
from app.core.config import settings

async def analyze_with_groq(screenshot_path: str) -> dict:
    """
    Analyze website screenshot using Groq Llama-4-Maverick 멀티모달 API.
    Args:
        screenshot_path: Path to the screenshot file
    Returns:
        dict: Analysis results with title, atmosphere, colors, and keywords
    Raises:
        Exception: If analysis fails
    """
    # 이미지 파일을 base64로 인코딩
    with open(screenshot_path, "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode("utf-8")

    prompt = """
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

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
    "model": settings.groq_model, # 반드시 llama-3.2-11b-vision-preview 등 비전 모델이어야 함
    "messages": [
        {
            "role": "system", 
            "content": "You are a world-class creative director and brand analyst."
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text", 
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{img_b64}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 1024,
    "temperature": 0.2
}
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"].strip()

    # 기존 파싱 로직 재사용
    if "```json" in text:
        text = text.split("```json")[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    text = text[text.find('{'):text.rfind('}')+1]
    try:
        analysis = json.loads(text)
        return analysis
    except json.JSONDecodeError as e:
        text = text.replace("'", '"').replace('\n', ' ')
        try:
            analysis = json.loads(text)
            return analysis
        except:
            raise Exception(f"Failed to parse Groq response as JSON: {text[:200]}")
