import pytest_asyncio
from typing import AsyncIterator
from redis.asyncio import Redis
from app.core import config


@pytest_asyncio.fixture
async def redis_client() -> AsyncIterator[Redis]:
    client = Redis.from_url(config.REDIS.URL)

    yield client

    await client.flushdb()
    await client.aclose()
