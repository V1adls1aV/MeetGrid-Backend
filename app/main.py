from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(api_router)
    yield


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOW_ORIGINS_LIST,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
