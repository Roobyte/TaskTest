from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import auth
from app.redis_client import redis_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await redis_client.ping()
    logger.info("Connected to Redis")
    yield

app = FastAPI(title="Auth Service", lifespan=lifespan)

app.include_router(auth.router)
