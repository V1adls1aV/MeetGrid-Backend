from typing import Callable

import inject
from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import WatchError

from app.core import config
from app.core.exceptions import InconsistencyError, TopicNotFoundError
from app.models import Topic


@inject.autoparams("redis")
async def save_topic(topic: Topic, redis: Redis, *, refresh_ttl: bool = False) -> None:
    await redis.set(
        f"topic:{topic.topic_id}",
        topic.model_dump_json(),
        ex=config.REDIS.TTL_SECONDS if refresh_ttl else None,
        keepttl=not refresh_ttl,
    )


@inject.autoparams("redis")
async def get_topic(topic_id: str, redis: Redis) -> Topic:
    data = await redis.get(f"topic:{topic_id}")
    if data is not None:
        return Topic.model_validate_json(data)
    raise TopicNotFoundError


@inject.autoparams("redis")
async def delete_topic(topic_id: str, redis: Redis) -> None:
    await redis.delete(f"topic:{topic_id}")


@inject.autoparams("redis")
async def patch_topic(
    topic_id: str,
    mutation: Callable[[Topic], None],
    redis: Redis,
    *,
    max_retries: int = config.REDIS.MAX_RETRY,
) -> Topic:
    key = f"topic:{topic_id}"
    for _ in range(max_retries):
        async with redis.pipeline() as pipe:
            try:
                await pipe.watch(key)
                topic = Topic.model_validate_json(await pipe.get(key))

                mutation(topic)

                pipe.multi()
                pipe.set(key, topic.model_dump_json())

                if await pipe.execute():
                    return topic
            except WatchError:
                continue
            except ValidationError:
                raise TopicNotFoundError
    raise InconsistencyError
