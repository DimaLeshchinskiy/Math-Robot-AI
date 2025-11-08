from fastapi import Depends, APIRouter
from app.services.auth_service import basic_auth

router = APIRouter()

@router.get("/test")
async def test(
    username: str = Depends(basic_auth)
) -> str:
    return "OK"