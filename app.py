"""
Gradio wrapper for HF Spaces compatibility
Mounts FastAPI app to Gradio for proper routing
"""
import gradio as gr
from app.main import app

# Mount FastAPI to Gradio
gradio_app = gr.mount_gradio_app(
    gr.Blocks(title="VIBE_LINK API"),
    app,
    path="/"
)
