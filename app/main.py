from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core import config
from app.core.di import configure_di
from app.core.exceptions import ServiceError, exception_handler
import inject
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.include_router(api_router)
    configure_di()

    yield

    await inject.instance(Redis).aclose()


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

app.add_exception_handler(ServiceError, exception_handler)
app.add_middleware(
    lambda app, *args, **kwargs: CORSMiddleware(app, *args, **kwargs),
    allow_origins=config.ALLOW_ORIGINS_LIST,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
