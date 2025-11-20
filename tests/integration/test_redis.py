from __future__ import annotations

from datetime import datetime

import pytest
from redis.asyncio import Redis

from app.core.exceptions import TopicNotFoundError
from app.db.redis import delete_topic, get_topic, patch_topic, save_topic
from app.models import Topic
from tests.unit.util import make_interval


def _topic(topic_id: str) -> Topic:
    now = datetime(2025, 1, 1, 9, 0)
    return Topic(
        topic_id=topic_id,
        topic_name="Standup",
        admin_name="Alice",
        description=None,
        constraints=[make_interval(now, hours=(0, 1))],
        votes={"bob": [make_interval(now, minutes=(0, 30))]},
        created_at=now,
    )


@pytest.mark.asyncio
async def test_save_and_get_topic_roundtrip(redis_client: Redis) -> None:
    stored = _topic("topic-roundtrip")

    await save_topic(stored, redis_client)
    loaded = await get_topic(stored.topic_id, redis_client)

    assert loaded == stored


@pytest.mark.asyncio
async def test_override_topic(redis_client: Redis) -> None:
    stored = _topic("topic-override")
    await save_topic(stored, redis_client)

    stored.topic_name = "New Name"
    await save_topic(stored, redis_client)

    loaded = await get_topic(stored.topic_id, redis_client)
    assert loaded.topic_name == stored.topic_name


@pytest.mark.asyncio
async def test_get_topic_missing_raises(redis_client: Redis) -> None:
    with pytest.raises(TopicNotFoundError):
        await get_topic("missing-topic", redis_client)


@pytest.mark.asyncio
async def test_delete_topic_removes_data(redis_client: Redis) -> None:
    stored = _topic("topic-deletion")
    await save_topic(stored, redis_client)

    await delete_topic(stored.topic_id, redis_client)

    with pytest.raises(TopicNotFoundError):
        await get_topic(stored.topic_id, redis_client)


@pytest.mark.asyncio
async def test_patch_topic_updates_data(redis_client: Redis) -> None:
    stored = _topic("topic-patch")
    await save_topic(stored, redis_client)

    def change_topic_name(topic: Topic) -> None:
        topic.topic_name = "New Name"

    await patch_topic(stored.topic_id, change_topic_name, redis_client)

    loaded = await get_topic(stored.topic_id, redis_client)
    assert loaded.topic_name == "New Name"


@pytest.mark.asyncio
async def test_patch_topic_raises_error_on_missing_topic(redis_client: Redis) -> None:
    with pytest.raises(TopicNotFoundError):
        await patch_topic(
            "missing-topic",
            lambda topic: None,
            redis_client,
        )
