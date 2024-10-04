# app/routers/health.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/check", summary="Health Check")
def health_check():
    """
    Health check endpoint to verify if the API is running.
    """
    return JSONResponse(content={"status": "ok", "message": "API is healthy."})
