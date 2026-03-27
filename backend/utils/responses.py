"""backend/utils/responses.py

Uniform JSON envelope helpers.

Every API response follows the same shape:
    {
        "status":  "success" | "error",
        "message": "...",
        "data":    { ... }   # only on success; empty dict on errors
    }
"""

from fastapi import HTTPException


def ok(data: dict = None, message: str = "OK") -> dict:
    """
    Build a successful response envelope.

    Args:
        data:    Dict of payload fields to return to the caller.
        message: Human-readable description of what happened.

    Returns:
        Response dict matching the standard envelope shape.
    """
    return {
        "status":  "success",
        "message": message,
        "data":    data or {},
    }


def fail(message: str, status_code: int = 400) -> HTTPException:
    """
    Build and raise an HTTP error with the standard envelope shape.

    Args:
        message:     User-facing error description.
        status_code: HTTP status code (default 400 Bad Request).

    Raises:
        HTTPException: FastAPI will serialise this into the HTTP response.
    """
    return HTTPException(
        status_code=status_code,
        detail={
            "status":  "error",
            "message": message,
            "data":    {},
        },
    )
