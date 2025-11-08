from fastapi import status, APIRouter
from app.schemas.status_schema import HealthResponse

router = APIRouter()

# Health check endpoint
@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    response_description="Service status information"
)
async def health_check():
    """Check if the service is running"""
    return {"status": "healthy"}