from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from api.services.audit import audit_service
from api.dependencies import get_api_key

router = APIRouter()

@router.get("/audit", dependencies=[Depends(get_api_key)])
async def get_audit_logs(
    session_id: Optional[str] = None,
    limit: int = Query(50, le=100)
):
    try:
        return audit_service.get_events(session_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
