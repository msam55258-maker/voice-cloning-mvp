"""backend/routes/upload.py

Route: POST /upload-voice
Handles voice sample uploads with strict validation.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File

from backend.config import settings
from backend.services import file_service
from backend.utils.logger import logger
from backend.utils.responses import ok, fail
from backend.utils.validators import assert_wav_magic_bytes, get_wav_duration

router = APIRouter(tags=["Upload"])

@router.post("/upload-voice")
async def upload_voice(file: UploadFile = File(...)):
    """Accept, validate, and store a WAV voice sample."""
    logger.info("POST /upload-voice | filename=%s | size=%s", file.filename, file.size)

    if not file.filename or not file.filename.lower().endswith(".wav"):
        raise fail("Invalid file type. Only .wav files are accepted.")

    content = await file.read()
    if not content:
        raise fail("Uploaded file is empty.")

    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise fail(f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB size limit.")

    try:
        assert_wav_magic_bytes(content)
    except ValueError as exc:
        raise fail(str(exc))

    # Save to temp for duration validation
    temp_path = os.path.join(settings.VOICES_DIR, f"_tmp_{uuid.uuid4()}.wav")
    try:
        with open(temp_path, "wb") as fh:
            fh.write(content)

        duration = get_wav_duration(temp_path)
        if duration < settings.MIN_AUDIO_DURATION_S:
            raise fail(f"Audio is too short ({duration:.1f} s). Min required: {settings.MIN_AUDIO_DURATION_S} s.")

        final_path = file_service.save_voice_sample(content)
        
        return ok(
            data={
                "voice_path": final_path,
                "duration_seconds": round(duration, 2),
            },
            message="Voice sample uploaded successfully."
        )

    except Exception as exc:
        logger.exception("Upload failed: %s", exc)
        raise fail(str(exc)) if not isinstance(exc, Exception) else exc

    finally:
        file_service.remove_file_if_exists(temp_path)
