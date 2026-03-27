"""backend/services/file_service.py

Handles all file-system operations for voices and outputs.
"""

import os
import uuid
from backend.config import settings
from backend.utils.logger import logger

def ensure_directories() -> None:
    """Create storage directories if they do not exist."""
    os.makedirs(settings.VOICES_DIR, exist_ok=True)
    os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
    logger.info("Storage directories ready: %s | %s", settings.VOICES_DIR, settings.OUTPUTS_DIR)

def save_voice_sample(content: bytes) -> str:
    """Persist raw WAV bytes as a unique file."""
    file_id = str(uuid.uuid4())
    filepath = os.path.join(settings.VOICES_DIR, f"voice_{file_id}.wav")

    with open(filepath, "wb") as fh:
        fh.write(content)

    logger.info("Voice sample saved: %s (%d bytes)", filepath, len(content))
    return filepath

def new_output_path() -> tuple[str, str]:
    """Generate a unique path for a new audio output file."""
    output_id = str(uuid.uuid4())
    filepath = os.path.join(settings.OUTPUTS_DIR, f"audio_{output_id}.wav")
    return output_id, filepath

def remove_file_if_exists(path: str) -> None:
    """Silently delete a file if it exists."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug("Cleaned up file: %s", path)
    except OSError as exc:
        logger.warning("Could not remove file %s: %s", path, exc)

def output_file_is_valid(path: str, min_bytes: int = 1024) -> bool:
    """Verify that a generated output file exists and is non-empty."""
    return os.path.isfile(path) and os.path.getsize(path) >= min_bytes
