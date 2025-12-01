from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class MaskRequest(BaseModel):
    text: str
    session_id: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UnmaskRequest(BaseModel):
    text: str
    session_id: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DetectRequest(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = Field(default_factory=dict)
