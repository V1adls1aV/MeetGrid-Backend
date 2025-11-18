from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router

ALLOW_ORIGINS = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(api_router)
    yield


app = FastAPI(title="MeetGrid Backend", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
