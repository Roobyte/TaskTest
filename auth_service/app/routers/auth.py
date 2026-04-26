import httpx
import time

from fastapi import APIRouter, Depends, HTTPException, Response
from redis.exceptions import RedisError
from pydantic import BaseModel

from app.config import settings
from app.jwt_utils import create_access_token, decode_token
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
async def login(
    payload: LoginRequest,
    response: Response,
    client: httpx.AsyncClient = Depends(get_http_client),
):
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
            try:
                data = resp.json()
            except ValueError:
                raise HTTPException(status_code=502, detail="Malformed user service response")
            user_id = data.get("id")
            if not user_id:
                raise HTTPException(status_code=502, detail="Malformed user service response")
        else:
            raise HTTPException(status_code=502, detail="User service error")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="User service unavailable")

    token = create_access_token(user_id)
    token_payload = decode_token(token)
    if not isinstance(token_payload, dict):
        raise HTTPException(status_code=500, detail="Token generation failed")

    jti = token_payload.get("jti")
    exp = token_payload.get("exp")
    if not isinstance(jti, str) or not isinstance(exp, (int, float)):
        raise HTTPException(status_code=500, detail="Token generation failed")

    ttl = int(exp - time.time())
    if ttl <= 0:
        raise HTTPException(status_code=500, detail="Token generation failed")

    try:
        await redis_client.setex(f"session:{jti}", ttl, user_id)
    except RedisError:
        raise HTTPException(status_code=503, detail="Auth storage unavailable")

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=ttl,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        path="/",
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response, payload: dict = Depends(get_current_user)):
    jti = payload["jti"]
    exp = payload["exp"]
    ttl = int(exp - time.time())
    try:
        if ttl > 0:
            await redis_client.setex(f"blacklist:{jti}", ttl, "1")
        await redis_client.delete(f"session:{jti}")
    except RedisError:
        raise HTTPException(status_code=503, detail="Auth storage unavailable")

    response.delete_cookie(key=settings.session_cookie_name, path="/")

    return {"msg": "Logged out"}


@router.get("/token/verify")
async def verify_token(payload: dict = Depends(get_current_user)):
    return {"user_id": payload["sub"]}
