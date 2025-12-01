from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class PIIEntity(BaseModel):
    type: str
    text: str
    start: int
    end: int
    score: float
    token: Optional[str] = None

class MaskResponse(BaseModel):
    success: bool
    masked_text: str
    entities: List[PIIEntity]
    session_id: str
    risk_score: float
    metadata: Optional[Dict[str, Any]] = None

class UnmaskResponse(BaseModel):
    success: bool
    unmasked_text: str
    entities_unmasked: List[Dict[str, Any]]
    audit_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DetectResponse(BaseModel):
    success: bool
    entities: List[PIIEntity]
    risk_score: float
    metadata: Optional[Dict[str, Any]] = None
