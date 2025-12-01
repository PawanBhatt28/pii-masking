from fastapi import APIRouter, HTTPException, Depends
from api.models.request import UnmaskRequest
from api.models.response import UnmaskResponse
from api.services.masking import masking_service
from api.dependencies import get_api_key

router = APIRouter()

@router.post("/unmask", response_model=UnmaskResponse, dependencies=[Depends(get_api_key)])
async def unmask_text(request: UnmaskRequest):
    try:
        return masking_service.unmask(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
