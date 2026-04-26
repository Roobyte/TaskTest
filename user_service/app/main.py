from fastapi import FastAPI
from app.routers import user
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("User service started")
    yield

app = FastAPI(title="User Service", lifespan=lifespan)
app.include_router(user.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
