from fastapi import APIRouter, HTTPException, Query
from api.services.audit import audit_service

router = APIRouter()

@router.get("/audit")
async def get_audit_logs(
    limit: int = Query(50, le=100)
):
    try:
        return audit_service.get_events(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
