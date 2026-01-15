---
title: VIBE_LINK Server
emoji: 🎨
colorFrom: gray
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🎨 VIBE_LINK Backend

AI-powered serverless API that transforms website URLs into stunning "Vibe Poster" images using Google Gemini and Hugging Face Flux.1.

## 🚀 Features

- **Screenshot Capture**: Headless Chrome (pyppeteer) for high-quality website screenshots
- **AI Analysis**: Google Gemini 2.5 Flash extracts design vibe and generates artistic prompts
- **Image Generation**: Hugging Face Flux.1-dev creates 3D abstract posters
- **Cloud Hosting**: ImgBB API for permanent image storage
- **Optimized**: Production-ready with minimal resource footprint

## 🏗️ Tech Stack

- **Framework**: FastAPI + Uvicorn
- **AI Models**: 
  - Google Gemini 2.0 Flash Exp (vision analysis)
  - FLUX.1-dev (image generation)
- **Infrastructure**: Docker (Hugging Face Spaces)
- **Language**: Python 3.9

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/Lcmind/vibe-link-backend.git
cd vibe-link-backend
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - HF_TOKEN (Hugging Face)
# - GEMINI_API_KEY (Google AI Studio)
# - IMGBB_KEY (ImgBB)
```

### 3. Run Locally (Docker)
```bash
docker build -t vibe-link-backend .
docker run -p 7860:7860 --env-file .env vibe-link-backend
```

### 4. Run Locally (Python)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 7860
```

## 🌐 API Usage

### POST /create
Generate a vibe poster from a website URL.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "poster_url": "https://i.ibb.co/abc123/poster.webp",
  "vibe": "Minimalist",
  "summary": "깔끔한 디자인과 명확한 타이포그래피가 돋보이는 현대적인 웹사이트"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "vibe-link-backend"
}
```

## 🎯 Deployment to Hugging Face Spaces

### 1. Create a New Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Select **Docker** as SDK
4. Name: `vibe-link-backend`

### 2. Push Code to HF Space
```bash
# Add Hugging Face as remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/vibe-link-backend
git push hf main
```

### 3. Configure Secrets
In Space Settings → Repository Secrets, add:
- `HF_TOKEN`
- `GEMINI_API_KEY`
- `IMGBB_KEY`

### 4. Access Your API
```
https://YOUR_USERNAME-vibe-link-backend.hf.space/
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | Hugging Face API token | ✅ |
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `IMGBB_KEY` | ImgBB API key | ✅ |

### Get API Keys
- **Hugging Face**: https://huggingface.co/settings/tokens
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **ImgBB**: https://api.imgbb.com/

## 📊 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ POST /create { "url": "https://example.com" }              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  STEP 1: Screenshot Capture     │
        │  Tool: pyppeteer                │
        │  Output: screenshot.jpg         │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  STEP 2: AI Analysis            │
        │  Tool: Google Gemini 2.5 Flash  │
        │  Output: vibe + flux_prompt     │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  STEP 3: Image Generation       │
        │  Tool: HF Flux.1-dev            │
        │  Output: poster.webp            │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  STEP 4: Upload to ImgBB        │
        │  Tool: ImgBB API                │
        │  Output: public URL             │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │  Response: { poster_url }       │
        └─────────────────────────────────┘
```

## 🛠️ Development

### Project Structure
```
vibe-link-backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # Documentation
```

### Code Quality Features
- ✅ Type hints (Pydantic models)
- ✅ Error handling & logging
- ✅ Resource cleanup (temp files)
- ✅ Docker health checks
- ✅ Production-ready CORS
- ✅ Memory-optimized Chrome args

## 📝 License

MIT License - feel free to use for your projects!

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📧 Support

For issues or questions, open a GitHub issue at:
https://github.com/Lcmind/vibe-link-backend/issues

---

**Built with ❤️ by S-Grade Developer**
