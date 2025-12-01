from fastapi import APIRouter
from api.services.vault import vault_service
from api.services.audit import audit_service

router = APIRouter()

@router.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "redis": "unknown",
            "mysql": "unknown"
        }
    }
    
    # Check Redis
    try:
        if vault_service.redis.ping():
            health_status["components"]["redis"] = "healthy"
    except Exception:
        health_status["components"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
        
    # Check MySQL
    try:
        if audit_service.pool:
            conn = audit_service.pool.get_connection()
            conn.ping()
            conn.close()
            health_status["components"]["mysql"] = "healthy"
        else:
            health_status["components"]["mysql"] = "unhealthy"
            health_status["status"] = "degraded"
    except Exception:
        health_status["components"]["mysql"] = "unhealthy"
        health_status["status"] = "degraded"
        
    return health_status
