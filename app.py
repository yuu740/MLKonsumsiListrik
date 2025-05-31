# app.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from gradio.routes import mount_gradio_app
from components import build_interface
import uvicorn
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app")

os.makedirs("maps", exist_ok=True)
logger.info(" 'maps' directory ensured to exist.")
app = FastAPI()

app.mount("/maps", StaticFiles(directory="maps"), name="maps")
logger.info("'/maps' static directory mounted.")

gradio_app = build_interface()
logger.info("Gradio interface built successfully.")

app = mount_gradio_app(app, gradio_app, path="/gradio")
logger.info("Gradio app mounted at '/gradio'.")

@app.get("/")
async def root():
    """Root endpoint to redirect users to the Gradio interface."""
    logger.info("Root endpoint accessed. Redirecting to /gradio.")
    return {"message": "Akses antarmuka clustering di /gradio"}

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 