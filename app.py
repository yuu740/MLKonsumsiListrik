# app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from gradio.routes import mount_gradio_app
import os

# Import your Gradio interface builder from a separate file
from components import build_interface

app = FastAPI()

# --- Configuration for serving temporary map files ---
# Define a directory to store temporary map files
STATIC_MAPS_DIR = "static_maps"
# Create the directory if it doesn't exist (important for Hugging Face Spaces initialization)
os.makedirs(STATIC_MAPS_DIR, exist_ok=True)

# Mount the static files directory.
# Files in STATIC_MAPS_DIR will be accessible via /maps/
app.mount("/maps", StaticFiles(directory=STATIC_MAPS_DIR), name="static_maps")

# --- Mount the Gradio app ---
# Build the Gradio interface
demo = build_interface()
# Mount the Gradio app under the /gradio path
app = mount_gradio_app(app, demo, path="/gradio")

# --- FastAPI Root Endpoint (Optional) ---
@app.get("/")
async def read_root():
    return {"message": "Welcome! Go to /gradio for the clustering visualization."}

# Important: For Hugging Face Spaces, you typically don't include
# `if __name__ == "__main__": uvicorn.run(app, ...)` in `app.py`.
# Hugging Face's environment will detect the `app` object and run it
# using Uvicorn internally based on your SDK configuration (e.g., "FastAPI").