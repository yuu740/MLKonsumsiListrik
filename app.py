# app.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from gradio.routes import mount_gradio_app
from components import build_interface


os.makedirs("maps", exist_ok=True)

base_app = FastAPI()
base_app.mount("/maps", StaticFiles(directory="maps"), name="maps")

gradio_app = build_interface()
app = mount_gradio_app(base_app, gradio_app, path="/")

@app.get("/")
async def root():
    return {"message": "Buka / untuk akses antarmuka clustering"}