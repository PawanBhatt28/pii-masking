from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any
from api.services.vault import vault_service
from api.dependencies import get_api_key

router = APIRouter()

@router.get("/admin/vault", dependencies=[Depends(get_api_key)])
async def list_vault_entries(limit: int = Query(50, le=100)):
    """
    List currently stored PII tokens in Redis (Debug/Admin endpoint).
    """
    try:
        return vault_service.get_all_entries(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
