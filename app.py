# app.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from gradio.routes import mount_gradio_app
from components import build_interface
import uvicorn


os.makedirs("maps", exist_ok=True)
app = FastAPI()

app.mount("/maps", StaticFiles(directory="maps"), name="maps")

gradio_app = build_interface()
print("Build interface success")
print("Building gradio app...")
app.mount("/gradio", gr.routes.App.create_app(gradio_app))

@app.get("/")
async def root():
    return {"message": "Buka /gradio untuk akses antarmuka clustering"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000)