from app.models import Topic
import inject
from redis.asyncio import Redis
from app.core.exceptions import TopicNotFoundError


@inject.autoparams("redis")
async def save_topic(topic: Topic, redis: Redis) -> None:
    await redis.set(f"topic:{topic.topic_id}", topic.model_dump_json())


@inject.autoparams("redis")
async def get_topic(topic_id: str, redis: Redis) -> Topic:
    data = await redis.get(f"topic:{topic_id}")
    if data is not None:
        return Topic.model_validate_json(data)
    raise TopicNotFoundError


@inject.autoparams("redis")
async def delete_topic(topic_id: str, redis: Redis) -> None:
    await redis.delete(f"topic:{topic_id}")
