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
당신은 세계적인 Creative Director입니다. 이 웹사이트 스크린샷을 분석하여, 
브랜드의 "바이브(vibe)"를 단 한 장의 포스터로 표현하기 위한 크리에이티브 전략을 제시하세요.

다음 형식의 JSON으로 정확히 답변하세요:
{
  "title": "브랜드를 대표하는 핵심 키워드 1-2단어 (영어)",
  "atmosphere": "브랜드 무드를 시각적으로 묘사 (30단어 이내, 영어)",
  "primary_color": "메인 컬러 (hex code)",
  "accent_color": "포인트 컬러 (hex code)", 
  "keywords": ["핵심 키워드1", "키워드2", "키워드3", "키워드4", "키워드5"]
}

분석 기준:
- 브랜드 정체성: 로고, 타이포그래피, 컬러 시스템
- 감성 톤: 차분함/에너지틱, 프로페셔널/친근함 등
- 시각 요소: 주요 색상, 레이아웃 스타일, 이미지 톤
- 타겟층: 추정되는 사용자 특성

JSON만 출력하세요. 다른 텍스트는 포함하지 마세요.
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
