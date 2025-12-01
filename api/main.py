from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config import settings

app = FastAPI(
    title="PII Shield API",
    description="Enterprise-grade PII masking and anonymization platform",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routers import mask, unmask, audit, health, admin

app.include_router(mask.router, prefix="/api/v1", tags=["Masking"])
app.include_router(unmask.router, prefix="/api/v1", tags=["Unmasking"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
app.mount("/static", StaticFiles(directory="ui"), name="static")

@app.get("/")
async def root():
    return FileResponse("ui/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
