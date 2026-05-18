import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from app.api.face import router as face_router
from app.api.arm import router as arm_router
from app.api.speech import router as speech_router

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {
        "message": "BeFast AI backend is running.",
        "camera_test_url": "/camera-test",
    }


@app.get("/camera-test")
async def camera_test():
    return FileResponse(STATIC_DIR / "camera-test.html")


app.include_router(face_router)
app.include_router(arm_router)
app.include_router(speech_router)
