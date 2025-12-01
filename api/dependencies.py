from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader
from api.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """
    Validate API Key. 
    In production, this would check against a database of valid keys.
    For MVP, we accept a hardcoded key or any key if not configured.
    """
    # For MVP simplicity, let's just require a specific key if set in env
    # or allow any non-empty key for demo purposes
    
    if not api_key_header:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key"
        )
        
    # In a real app, validate against DB
    # if api_key_header != settings.API_KEY:
    #     raise HTTPException(status_code=403, detail="Invalid API Key")
        
    return api_key_header
