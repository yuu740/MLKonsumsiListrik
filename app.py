# app.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from gradio.routes import mount_gradio_app
import os


from components import build_interface

STATIC_MAPS_DIR = "static_maps"
os.makedirs(STATIC_MAPS_DIR, exist_ok=True)

base_app = FastAPI()
base_app.mount("/maps", StaticFiles(directory=STATIC_MAPS_DIR), name="static_maps")

demo = build_interface()
app = mount_gradio_app(base_app, demo, path="/gradio")

@app.get("/")
async def read_root():
    return {"message": "Welcome! Go to /gradio for the clustering visualization."}

app