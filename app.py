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

app = FastAPI()

os.makedirs("maps", exist_ok=True)
logger.info(" 'maps' directory ensured to exist.")

app.mount("/maps", StaticFiles(directory="maps"), name="maps")
logger.info("'/maps' static directory mounted.")

gradio_app = build_interface()
logger.info("Gradio interface built successfully.")

app = mount_gradio_app(app, gradio_app, path="")
logger.info("Gradio app mounted at '/'.")

if __name__ == "__main__":
    logger.info("Starting Uvicorn server...")
    uvicorn.run("app:app", host="0.0.0.0", port=7860) 