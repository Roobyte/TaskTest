import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.config import settings
from app.jwt_utils import create_access_token
from app.dependencies import get_current_user
from app.redis_client import redis_client

router = APIRouter(prefix="", tags=["auth"])

class LoginRequest(BaseModel):
    login: str
    password: str

async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

@router.post("/login")
async def login(payload: LoginRequest, client: httpx.AsyncClient = Depends(get_http_client)):
    try:
        resp = await client.post(
            f"{settings.user_service_url}/check",
            json={"login": payload.login, "password": payload.password}
        )
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        elif resp.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        elif resp.status_code == 200:
            data = resp.json()
            user_id = data.get("id")
            if not user_id:
                raise HTTPException(status_code=502, detail="Malformed user service response")
        else:
            raise HTTPException(status_code=502, detail="User service error")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")

    token = create_access_token(user_id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/logout")
async def logout(payload: dict = Depends(get_current_user)):
    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti and exp:
        import time
        ttl = int(exp - time.time())
        if ttl > 0:
            await redis_client.setex(f"blacklist:{jti}", ttl, "1")
    return {"msg": "Logged out"}

@router.get("/token/verify")
async def verify_token(payload: dict = Depends(get_current_user)):
    return {"user_id": payload["sub"]}
