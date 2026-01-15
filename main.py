"""
VIBE_LINK Backend API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Serverless-style FastAPI backend for converting websites into Vibe Posters.
Optimized for Hugging Face Spaces (Docker SDK) with 16GB RAM.

Architecture:
    1. Screenshot Capture → pyppeteer (Headless Chrome)
    2. AI Analysis → Google Gemini 2.5 Flash
    3. Image Generation → Hugging Face Flux.1-dev
    4. Image Hosting → ImgBB API

Author: S-Grade Developer | Production-Ready Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import json
import base64
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Dict
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from pyppeteer import launch
from huggingface_hub import InferenceClient
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION & ENVIRONMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

load_dotenv()

# API Keys (Secured via Environment Variables)
HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMGBB_KEY = os.getenv("IMGBB_KEY")

# Validate API Keys
if not all([HF_TOKEN, GEMINI_API_KEY, IMGBB_KEY]):
    raise RuntimeError(
        "Missing API Keys! Set HF_TOKEN, GEMINI_API_KEY, IMGBB_KEY in environment."
    )

# Initialize AI Services
genai.configure(api_key=GEMINI_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# Prevent pyppeteer from downloading Chromium (use system-installed one)
os.environ['PUPPETEER_SKIP_CHROMIUM_DOWNLOAD'] = 'true'
os.environ['PUPPETEER_EXECUTABLE_PATH'] = '/usr/bin/chromium'

# Constants
SCREENSHOT_TIMEOUT = 20000  # 20 seconds
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 1200
FLUX_MODEL = "black-forest-labs/FLUX.1-schnell"  # Faster model, same quality (4 steps vs 30)
TEMP_DIR = Path(tempfile.gettempdir()) / "vibe_link"
TEMP_DIR.mkdir(exist_ok=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PYDANTIC MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CreateRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target website URL to analyze")


class CreateResponse(BaseModel):
    status: str
    poster_url: str
    vibe: Optional[str] = None
    summary: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FASTAPI LIFECYCLE MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage browser lifecycle to minimize resource usage"""
    print("🚀 VIBE_LINK Backend Starting...")
    yield
    print("🛑 Cleaning up resources...")
    # Cleanup temp files on shutdown
    for file in TEMP_DIR.glob("*"):
        try:
            file.unlink()
        except Exception:
            pass


app = FastAPI(
    title="VIBE_LINK API",
    description="AI-powered Website to Vibe Poster Generator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (Allow all origins for public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CORE PIPELINE FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def capture_screenshot(url: str) -> Path:
    """
    STEP 1: Screenshot Capture
    Uses Headless Chrome to capture website screenshot.
    Optimized for Docker environment with sandbox disabled.
    """
    screenshot_path = TEMP_DIR / f"screenshot_{id(url)}.jpg"
    
    browser = None
    try:
        # Launch Chromium with Docker-safe arguments
        browser = await launch(
            headless=True,
            executablePath="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-extensions",
                "--single-process",  # Memory optimization
            ],
        )
        
        page = await browser.newPage()
        await page.setViewport({"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT})
        
        # Navigate with timeout
        await page.goto(
            url,
            {"waitUntil": "domcontentloaded", "timeout": SCREENSHOT_TIMEOUT}
        )
        
        # Capture screenshot
        await page.screenshot({"path": str(screenshot_path), "type": "jpeg", "quality": 85})
        
        return screenshot_path
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Screenshot capture failed: {str(e)}"
        )
    finally:
        if browser:
            await browser.close()


async def analyze_with_gemini(screenshot_path: Path) -> Dict[str, str]:
    """
    STEP 2: AI Analysis
    Uses Google Gemini 2.5 Flash to analyze screenshot and generate
    vibe description + image generation prompt.
    """
    try:
        # Upload image to Gemini
        uploaded_file = genai.upload_file(str(screenshot_path))
        
        # AI Analysis Prompt
        analysis_prompt = """
        You are a world-class Creative Director and Prompt Engineer.
        Analyze this website screenshot and generate a high-end vertical brand poster concept for Flux.1.

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        STEP 1: EXTRACT BRAND IDENTITY
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. Find the main brand name/logo in the screenshot.
        2. **CRITICAL: Convert Korean to English romanization.**
           Examples:
           - "무신사" → "MUSINSA"
           - "떡볶이 천국" → "TTEOKBOKKI HEAVEN"
           - "이창민" → "LEE CHANGMIN"
           - "카페 서울" → "CAFE SEOUL"
        3. If no brand name exists, use the domain name.

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        STEP 2: ANALYZE BUSINESS TYPE & VISUAL DNA
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Identify the business category and extract visual elements:
        
        **Business Examples:**
        - Fashion (무신사) → Clothes, fabrics, hangers, runway
        - Food (떡볶이) → Ingredients, steam, spices, bowls
        - Tech (코딩) → Code snippets, circuits, data streams
        - Fitness (헬스장) → Dumbbells, protein, energy
        - Corporate (법률) → Books, marble, gold, scales
        
        **Extract:**
        - Dominant Color Palette (2-3 colors)
        - Key Physical Objects (what fills the background)
        - Material/Texture (fabric, metal, food, digital)
        - Lighting Mood (neon, sunlight, studio, dark)

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        STEP 3: CONSTRUCT FLUX.1 PROMPT
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Build a detailed scene description:

        **BACKGROUND (70% of prompt):**
        - Describe a 3D environment FILLED with objects related to the business.
        - Example (Fashion): "floating designer clothes, silk fabrics, leather jackets, sneakers, accessories scattered in mid-air"
        - Example (Food): "steaming bowls, fresh ingredients, spices exploding, sauce splash, vibrant colors"
        - Use the dominant colors extracted in Step 2.

        **CENTER TYPOGRAPHY (30% of prompt):**
        - Place the ENGLISH brand name in the CENTER.
        - Make it a 3D object matching the theme:
          * Fashion: "metallic chrome letters with fabric texture"
          * Food: "letters made of the food itself (cookies, cake, rice)"
          * Tech: "neon holographic glowing text"
        - Keywords: "big bold 3D typography", "magazine cover layout", "centered composition"

        **MANDATORY RULES:**
        ✅ NO Korean characters (Hangul) - Flux CANNOT render them
        ✅ Convert all Korean to English romanization
        ✅ Brand name must be in CENTER in big 3D letters
        ✅ Background must be FILLED with thematic 3D objects
        ✅ Use "vertical poster", "9:16 aspect ratio", "high quality 3D render"

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        OUTPUT FORMAT (JSON)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Return ONLY valid JSON:
        {
            "vibe": "Business type in 1-2 English words (e.g., Fashion, Spicy Food, Tech)",
            "summary": "One sentence description in Korean",
            "flux_prompt": "Complete Flux.1 prompt in English following the rules above"
        }

        **Example flux_prompt structure:**
        "A vertical 3D poster (9:16), [BACKGROUND: detailed scene with thematic objects], centered big bold 3D typography text '[BRAND NAME IN ENGLISH]' made of [material matching theme], [lighting description], magazine cover layout, high quality render, cinematic composition"
        """
        
        # Call Gemini API
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content([uploaded_file, analysis_prompt])
        
        # Robust JSON parsing with multiple fallback strategies
        response_text = response.text.strip()
        
        # Strategy 1: Remove markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
        
        # Strategy 2: Find JSON object between curly braces
        if not response_text.startswith("{"):
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]
        
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Gemini JSON response: {e}. Response: {response_text[:200]}")
        
        # Validate required fields
        if not all(k in analysis for k in ["vibe", "summary", "flux_prompt"]):
            raise ValueError(f"Missing required fields in Gemini response. Got: {list(analysis.keys())}")
            
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI analysis failed: {str(e)}"
        )


async def generate_poster(flux_prompt: str) -> Path:
    """
    STEP 3: Image Generation
    Uses Hugging Face Inference API with Flux.1-dev model
    to generate vibe poster.
    """
    poster_path = TEMP_DIR / f"poster_{id(flux_prompt)}.webp"
    
    try:
        # Call Flux.1-schnell via HF Inference API
        # Schnell is 10x faster than dev with similar quality
        image = hf_client.text_to_image(
            flux_prompt,
            model=FLUX_MODEL,
            # Parameters optimized for vertical poster
            width=768,
            height=1344,  # 9:16 aspect ratio
            num_inference_steps=4,  # Schnell optimized for 1-4 steps
        )
        
        # Save as WebP for optimal compression
        image.save(str(poster_path), "WEBP", quality=90, method=6)
        
        return poster_path
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image generation failed: {str(e)}"
        )


async def upload_to_imgbb(image_path: Path) -> str:
    """
    STEP 4: Image Hosting
    Uploads generated poster to ImgBB for permanent hosting.
    Returns public URL.
    """
    try:
        # Read image and encode as base64
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # Upload to ImgBB
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": IMGBB_KEY,
                "image": image_data,
                "expiration": 0,  # Never expire
            },
            timeout=30,
        )
        
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success"):
            raise ValueError("ImgBB upload failed")
            
        return result["data"]["url"]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )
    finally:
        # Clean up local file immediately after upload
        try:
            image_path.unlink()
        except Exception:
            pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get("/")
async def root():
    """API Root - Health & Info"""
    return {
        "service": "VIBE_LINK API",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "create": "POST /create - Generate vibe poster from URL",
            "health": "GET /health - Service health check",
        },
    }


@app.get("/health")
async def health_check():
    """Health Check Endpoint (for Docker HEALTHCHECK)"""
    return {"status": "healthy", "service": "vibe-link-backend"}


@app.post("/create", response_model=CreateResponse, responses={500: {"model": ErrorResponse}})
async def create_vibe_poster(request: CreateRequest):
    """
    🎨 Main Endpoint: Generate Vibe Poster
    
    Pipeline:
        1. Capture screenshot of website
        2. Analyze with Gemini AI
        3. Generate poster with Flux.1
        4. Upload to ImgBB
        
    Returns:
        CreateResponse with poster URL and metadata
    """
    screenshot_path = None
    
    try:
        # STEP 1: Screenshot
        print(f"📸 Capturing screenshot: {request.url}")
        screenshot_path = await capture_screenshot(str(request.url))
        
        # STEP 2: AI Analysis
        print("🧠 Analyzing with Gemini...")
        analysis = await analyze_with_gemini(screenshot_path)
        
        # STEP 3: Generate Poster
        print("🎨 Generating poster with Flux.1...")
        poster_path = await generate_poster(analysis["flux_prompt"])
        
        # STEP 4: Upload to ImgBB
        print("☁️ Uploading to ImgBB...")
        poster_url = await upload_to_imgbb(poster_path)
        
        print(f"✅ Success! Poster URL: {poster_url}")
        
        return CreateResponse(
            status="success",
            poster_url=poster_url,
            vibe=analysis["vibe"],
            summary=analysis["summary"],
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        # Cleanup screenshot file
        if screenshot_path and screenshot_path.exists():
            try:
                screenshot_path.unlink()
            except Exception:
                pass


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global error handler for unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc),
        },
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info",
    )
