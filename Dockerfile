# VIBE_LINK Backend - Optimized Production Dockerfile
# Designed for Hugging Face Spaces with Headless Chrome support

FROM python:3.9-slim

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Chromium (minimal set)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome environment variables
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Create app directory with proper permissions
WORKDIR /app
RUN chmod 777 /app

# Copy dependency files first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Hugging Face Spaces port
EXPOSE 7860

# Health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health', timeout=5)"

# Run FastAPI with production settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
