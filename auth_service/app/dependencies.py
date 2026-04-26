from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.jwt_utils import decode_token
from app.redis_client import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    jti = payload.get("jti")
    if jti:
        blacklisted = await redis_client.get(f"blacklist:{jti}")
        if blacklisted:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
    return payload
