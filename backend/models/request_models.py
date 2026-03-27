"""backend/models/request_models.py

Pydantic models for incoming API payloads.
Centralizing these ensures consistent validation across routes.
"""

from pydantic import BaseModel, Field, field_validator
from backend.config import settings
from backend.utils.validators import is_path_safe

class GenerateRequest(BaseModel):
    """Payload for audio synthesis requests."""
    
    text: str = Field(
        ..., 
        min_length=settings.MIN_TEXT_CHARS, 
        max_length=settings.MAX_TEXT_CHARS,
        description=f"Text to synthesise ({settings.MIN_TEXT_CHARS}-{settings.MAX_TEXT_CHARS} chars)."
    )
    voice_path: str = Field(
        ..., 
        description="Path to the uploaded voice sample returned by /upload-voice."
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        """Reject whitespace-only strings."""
        if not v.strip():
            raise ValueError("text must not be blank or whitespace-only.")
        return v

    @field_validator("voice_path")
    @classmethod
    def voice_path_must_be_safe(cls, v: str) -> str:
        """Reject paths that attempt to escape the permitted voices directory."""
        if not is_path_safe(str(settings.VOICES_DIR), v):
            raise ValueError("voice_path points outside the permitted voices directory.")
        return v
