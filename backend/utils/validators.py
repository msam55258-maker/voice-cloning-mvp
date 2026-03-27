"""backend/utils/validators.py

Low-level WAV file validation utilities.

These helpers are intentionally pure functions with no FastAPI
dependencies — they operate on file paths and raise plain
ValueError, making them easy to unit test in isolation.
"""

import contextlib
import os
import wave


def assert_wav_magic_bytes(content: bytes) -> None:
    """
    Check that raw file bytes start with the RIFF/WAVE header.

    WAV files always begin with:
        bytes 0-3  : "RIFF"
        bytes 8-11 : "WAVE"

    Args:
        content: Raw bytes of the uploaded file.

    Raises:
        ValueError: If the bytes do not match the expected WAV signature.
    """
    if not (content[:4] == b"RIFF" and content[8:12] == b"WAVE"):
        raise ValueError(
            "File does not appear to be a valid WAV file (bad RIFF/WAVE header)."
        )


def get_wav_duration(path: str) -> float:
    """
    Open a saved WAV file and return its duration in seconds.

    Args:
        path: Absolute or relative path to the .wav file on disk.

    Returns:
        Duration in seconds as a float.

    Raises:
        ValueError: If the file cannot be parsed as a valid WAV or has
                    corrupt/zero metadata fields.
    """
    try:
        with contextlib.closing(wave.open(path, "rb")) as wf:
            frames    = wf.getnframes()
            rate      = wf.getframerate()
            channels  = wf.getnchannels()
            sampwidth = wf.getsampwidth()

            if rate == 0 or channels == 0 or sampwidth == 0:
                raise ValueError("WAV header contains invalid (zero) metadata fields.")

            return frames / float(rate)

    except wave.Error as exc:
        raise ValueError(f"Could not read WAV file: {exc}") from exc


def is_path_safe(base_dir: str, candidate_path: str) -> bool:
    """
    Guard against directory-traversal attacks.

    Resolves both paths to their real absolute form and checks
    that the candidate resides within the permitted base directory.

    Args:
        base_dir:       The directory that all access should be confined to.
        candidate_path: The user-supplied path to validate.

    Returns:
        True if the path is safely within base_dir, False otherwise.
    """
    resolved_base      = os.path.realpath(base_dir)
    resolved_candidate = os.path.realpath(candidate_path)
    return resolved_candidate.startswith(resolved_base + os.sep) or \
           resolved_candidate == resolved_base
