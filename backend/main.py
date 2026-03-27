"""
backend/main.py — Application entrypoint
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import upload, generate   # update upload import
from backend.services import file_service, tts_service
from backend.utils.logger import logger

app = FastAPI(
    title="Voice Cloning MVP API",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    logger.info("→ %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Server error.", "data": {}},
        )
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("← %d  %.1f ms", response.status_code, elapsed_ms)
    return response

@app.on_event("startup")
async def on_startup():
    file_service.ensure_directories()
    tts_service.load_model()

app.include_router(upload.router)
app.include_router(generate.router)

@app.get("/", tags=["Health"])
async def health():
    return {
        "status": "success",
        "data": {"model_loaded": tts_service.is_model_ready()},
    }
