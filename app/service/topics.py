from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from nanoid import generate

from app.core import config
from app.core.exceptions import ForbiddenActionError
from app.db import redis as topic_repo
from app.models import (
    ConstraintsPayload,
    Topic,
    TopicCreate,
    TopicStats,
    VotePayload,
)
from app.service.topic_stats import build_topic_stats

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


async def create_topic(admin_name: str, payload: TopicCreate) -> Topic:
    """Persists a freshly created topic and returns it."""
    topic = Topic(
        topic_id=generate(size=config.GRID.TOPIC_ID_LENGTH),
        topic_name=payload.topic_name,
        admin_name=admin_name,
        description=payload.description,
        constraints=list(payload.constraints),
        votes={},
        created_at=_now_moscow(),
    )
    await topic_repo.save_topic(topic, refresh_ttl=True)
    return topic


async def get_topic_with_stats(topic_id: str) -> tuple[Topic, TopicStats]:
    """Loads topic and builds ladder stats for responses."""
    topic = await topic_repo.get_topic(topic_id)
    return topic, build_topic_stats(topic)


async def replace_vote(
    topic_id: str, username: str, payload: VotePayload
) -> tuple[Topic, TopicStats]:
    """Overwrites user vote and returns updated snapshot."""
    topic = await topic_repo.get_topic(topic_id)
    topic.votes[username] = list(payload.intervals)
    await topic_repo.save_topic(topic)
    return topic, build_topic_stats(topic)


async def overwrite_constraints(
    topic_id: str, username: str, payload: ConstraintsPayload
) -> tuple[Topic, TopicStats]:
    """Allows admin to replace constraints and get updated stats."""
    topic = await topic_repo.get_topic(topic_id)
    if topic.admin_name != username:
        raise ForbiddenActionError("Only topic admin can edit constraints.")
    topic.constraints = list(payload.constraints)
    await topic_repo.save_topic(topic)
    return topic, build_topic_stats(topic)


def _now_moscow() -> datetime:
    return datetime.now(MOSCOW_TZ)
