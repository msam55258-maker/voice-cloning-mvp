"""backend/models/response_models.py

Standardized API response shapes.
Every response from the server follows this envelope structure.
"""

from typing import Any, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    """
    Uniform JSON envelope for all successful and error responses.
    
    Shape:
        {
            "status":  "success" | "error",
            "message": "Human-readable description",
            "data":    { ... }
        }
    """
    status: str
    message: str
    data: Optional[Any] = {}
