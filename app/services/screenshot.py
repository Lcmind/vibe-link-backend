"""Screenshot capture service using Pyppeteer with Stealth Setup."""

import asyncio
import os
import logging
from pyppeteer import launch
from app.core.config import settings

logger = logging.getLogger(__name__)


async def capture_screenshot(url: str) -> tuple[str, str]:
    """
    Capture a screenshot of the given URL with stealth setup.
    
    Phase 1: Stealth Setup (위장)
    - User-Agent를 최신 Mac Chrome으로 위조
    - 1920x1080 뷰포트 강제 고정
    
    Phase 2: 침투 (Navigation)
    - domcontentloaded 전략 (10초 타임아웃)
    
    Phase 3: 시각 데이터 수집 (Screenshot)
    - fullPage=False (첫 화면 히어로 섹션만)
    - PNG 포맷 (색상 손실 방지)
    
    Phase 4: 문맥 데이터 수집 (DOM Text)
    - document.body.innerText로 사람 눈에 보이는 텍스트만 추출
    - 3000-4000자로 다이어트
    
    Args:
        url: Website URL to capture
        
    Returns:
        tuple[str, str]: (screenshot_path, extracted_text)
        
    Raises:
        Exception: If screenshot capture fails
    """
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    # Set environment variables for Pyppeteer
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1181205'
    os.environ['PYPPETEER_EXECUTABLE_PATH'] = settings.puppeteer_executable_path
    
    browser = None
    try:
        # === Phase 1: Stealth Setup ===
        browser = await launch(
            headless=True,
            executablePath=settings.puppeteer_executable_path,
            args=settings.puppeteer_args + [
                '--disable-blink-features=AutomationControlled',  # 봇 감지 차단
            ]
        )
        
        page = await browser.newPage()
        
        # User-Agent 위조: 최신 맥북 크롬 유저로 위장
        await page.setUserAgent(
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/122.0.0.0 Safari/537.36'
        )
        
        # 뷰포트 강제 고정: 1920x1080 (FHD)
        await page.setViewport({'width': 1920, 'height': 1080})
        
        # 봇 탐지 방지: navigator.webdriver 제거
        await page.evaluateOnNewDocument(
            '() => { Object.defineProperty(navigator, "webdriver", {get: () => undefined}) }'
        )
        
        # === Phase 2: 침투 (Navigation) ===
        try:
            # domcontentloaded: HTML 뼈대만 로딩되면 진행 (10초 타임아웃)
            await page.goto(url, {'waitUntil': 'domcontentloaded', 'timeout': 10000})
        except Exception as e:
            logger.warning(f"Navigation timeout or error: {e}, proceeding with current state")
            # 타임아웃 되어도 그때까지 로딩된 것으로 진행
        
        # === Phase 3: 시각 데이터 수집 (Screenshot) ===
        screenshot_path = '/tmp/screenshot.png'
        await page.screenshot({
            'path': screenshot_path,
            'fullPage': False,  # 첫 화면 히어로 섹션만
            'type': 'png'  # 색상 손실 방지
        })
        logger.info(f"[SCREENSHOT] Captured: {url}")
        
        # === Phase 4: 문맥 데이터 수집 (DOM Text) ===
        # document.body.innerText로 사람 눈에 보이는 텍스트만 추출
        extracted_text = await page.evaluate('() => document.body.innerText')
        
        # 데이터 다이어트: 공백 정리 + 3000-4000자로 제한
        if extracted_text:
            # 연속된 공백/줄바꿈을 1칸으로 정리
            cleaned_text = ' '.join(extracted_text.split())
            # 앞에서 3500자만 추출 (핵심 가치는 무조건 상단에 있음)
            extracted_text = cleaned_text[:3500]
            logger.info(f"[DOM TEXT] Extracted {len(extracted_text)} chars")
        else:
            extracted_text = ""
            logger.warning("[DOM TEXT] No text extracted")
        
        return screenshot_path, extracted_text
        
    finally:
        if browser:
            await browser.close()
