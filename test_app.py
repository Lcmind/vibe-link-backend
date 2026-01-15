"""Simple test app to verify HF Spaces setup."""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "working", "message": "Test app is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
