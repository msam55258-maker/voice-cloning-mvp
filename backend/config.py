"""
backend/config.py

All runtime settings are read from environment variables.
Defaults are provided for local development.

Usage:
    from backend.config import settings
    print(settings.VOICES_DIR)
"""

import os
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Settings:
    # ── Directories ────────────────────────────────────────────────
    BASE_DIR:    Path = Path(__file__).parent.parent   # project root
    VOICES_DIR:  Path = field(default_factory=lambda: Path(os.getenv("VOICES_DIR",  "backend/voices")))
    OUTPUTS_DIR: Path = field(default_factory=lambda: Path(os.getenv("OUTPUTS_DIR", "backend/outputs")))

    # ── Upload validation ──────────────────────────────────────────
    MAX_FILE_SIZE_MB:     float = float(os.getenv("MAX_FILE_SIZE_MB",     "10"))
    MIN_AUDIO_DURATION_S: float = float(os.getenv("MIN_AUDIO_DURATION_S", "3"))

    # ── Text generation limits ─────────────────────────────────────
    MAX_TEXT_CHARS: int = int(os.getenv("MAX_TEXT_CHARS", "500"))
    MIN_TEXT_CHARS: int = int(os.getenv("MIN_TEXT_CHARS", "10"))

    # ── XTTS model ─────────────────────────────────────────────────
    TTS_MODEL_NAME: str = os.getenv("TTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2")
    TTS_LANGUAGE:   str = os.getenv("TTS_LANGUAGE",   "en")

    # ── Derived convenience props ──────────────────────────────────
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        return int(self.MAX_FILE_SIZE_MB * 1024 * 1024)


# Singleton — import and use anywhere in the package
settings = Settings()
