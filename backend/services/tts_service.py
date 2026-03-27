"""backend/services/tts_service.py

Encapsulates all XTTS v2 model interactions.
"""

import torch
from backend.config import settings
from backend.utils.logger import logger

# ── PyTorch 2.6 compatibility patch ──────────────────────────────────────────
_original_torch_load = torch.load

def _permissive_torch_load(*args, **kwargs):
    kwargs.setdefault("weights_only", False)
    return _original_torch_load(*args, **kwargs)

torch.load = _permissive_torch_load

# ── Lazy import ──────────────────────────────────────────────────────────────
_TTS_CLASS = None
try:
    from TTS.api import TTS as _TTS_CLASS
except ImportError:
    logger.warning("Coqui TTS package not installed. Generation will fail.")

# ── Model Singleton ──────────────────────────────────────────────────────────
_model = None

def load_model() -> None:
    """Load the XTTS v2 model into memory."""
    global _model

    if _TTS_CLASS is None:
        logger.error("TTS package missing — skipping model load.")
        return

    logger.info("Loading TTS model: %s", settings.TTS_MODEL_NAME)
    try:
        _model = _TTS_CLASS(settings.TTS_MODEL_NAME)
        logger.info("✓ TTS model loaded successfully.")
    except Exception as exc:
        logger.exception("Failed to load TTS model: %s", exc)

def is_model_ready() -> bool:
    """Return True if the model has been loaded."""
    return _model is not None

def synthesise(text: str, speaker_wav: str, output_path: str) -> None:
    """Generate speech audio and write it to output_path."""
    if _model is None:
        raise RuntimeError("TTS model is not loaded.")

    logger.info("Synthesising audio | text_len=%d | speaker=%s", len(text), speaker_wav)

    _model.tts_to_file(
        text=text,
        speaker_wav=speaker_wav,
        language=settings.TTS_LANGUAGE,
        file_path=output_path,
    )
