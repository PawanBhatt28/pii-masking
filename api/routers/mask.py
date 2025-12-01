from fastapi import APIRouter, HTTPException, Depends
from api.models.request import MaskRequest
from api.models.response import MaskResponse
from api.services.masking import masking_service
from api.dependencies import get_api_key

router = APIRouter()

@router.post("/mask", response_model=MaskResponse, dependencies=[Depends(get_api_key)])
async def mask_text(request: MaskRequest):
    try:
        return masking_service.mask(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
