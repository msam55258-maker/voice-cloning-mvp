"""backend/routes/generate.py

Routes for audio synthesis and file serving.
"""

import os
import time
from fastapi import APIRouter
from fastapi.responses import FileResponse

from backend.config import settings
from backend.services import tts_service, file_service
from backend.models.request_models import GenerateRequest
from backend.utils.logger import logger
from backend.utils.responses import ok, fail

router = APIRouter(tags=["Generation"])

@router.post("/generate")
async def generate_audio(request: GenerateRequest):
    """Synthesise speech from text using a voice sample."""
    if not tts_service.is_model_ready():
        raise fail("TTS model is not available.", status_code=503)

    if not os.path.isfile(request.voice_path):
        raise fail("Voice sample not found.", status_code=404)

    output_id, output_path = file_service.new_output_path()
    start_time = time.perf_counter()

    try:
        tts_service.synthesise(
            text=request.text, 
            speaker_wav=request.voice_path, 
            output_path=output_path
        )
    except Exception as exc:
        file_service.remove_file_if_exists(output_path)
        logger.exception("Synthesis failed: %s", exc)
        raise fail("Audio generation failed.", status_code=500)

    elapsed = round(time.perf_counter() - start_time, 2)

    if not file_service.output_file_is_valid(output_path):
        file_service.remove_file_if_exists(output_path)
        raise fail("Synthesis produced an invalid file.", status_code=500)

    return ok(
        data={
            "audio_url": f"/outputs/audio_{output_id}.wav",
            "processing_time_seconds": elapsed,
        },
        message="Audio generated successfully."
    )

@router.get("/outputs/{filename}")
async def serve_audio(filename: str):
    """Serve a generated WAV file."""
    if any(sep in filename for sep in (os.sep, "/", "..")):
        raise fail("Invalid filename.", status_code=400)

    filepath = os.path.join(settings.OUTPUTS_DIR, filename)

    if not os.path.isfile(filepath):
        raise fail(f"Audio file '{filename}' not found.", status_code=404)

    return FileResponse(filepath, media_type="audio/wav", filename=filename)
