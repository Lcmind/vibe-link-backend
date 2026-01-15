# VIBE_LINK Backend - Optimized Production Dockerfile
# Designed for Hugging Face Spaces with Headless Chrome support

FROM python:3.11-slim

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

# HF Spaces requirement: Create user with UID 1000
RUN useradd -m -u 1000 user

# Set working directory
WORKDIR /app

# Copy requirements
COPY --chown=user requirements.txt .

# Install dependencies (as root, faster)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=user . /app

# Switch to user AFTER all installs
USER user

# Set user environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app

# Expose port
EXPOSE 7860

# Run simple test app first to verify HF Spaces setup
CMD ["uvicorn", "test_app:app", "--host", "0.0.0.0", "--port", "7860"]
