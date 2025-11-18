from contextlib import asynccontextmanager

import inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api import api_router, docs_router
from app.core import config
from app.core.di import configure_di
from app.core.exceptions import ServiceError, exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(api_router)
    app.include_router(docs_router)
    configure_di()

    yield

    await inject.instance(Redis).aclose()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)


app.add_exception_handler(ServiceError, exception_handler)  # type: ignore
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=config.ALLOW_ORIGINS_LIST,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
