"""Screenshot capture service using Pyppeteer."""

import asyncio
import os
from pyppeteer import launch
from app.core.config import settings


async def capture_screenshot(url: str) -> str:
    """
    Capture a screenshot of the given URL.
    
    Args:
        url: Website URL to capture
        
    Returns:
        str: Path to the saved screenshot
        
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
        browser = await launch(
            headless=True,
            executablePath=settings.puppeteer_executable_path,
            args=settings.puppeteer_args
        )
        
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        
        try:
            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': 30000})
        except Exception:
            # Fallback to domcontentloaded if networkidle0 times out
            await page.goto(url, {'waitUntil': 'domcontentloaded', 'timeout': 30000})
        
        screenshot_path = '/tmp/screenshot.png'
        await page.screenshot({'path': screenshot_path, 'fullPage': False})
        
        return screenshot_path
        
    finally:
        if browser:
            await browser.close()
