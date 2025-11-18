from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.interval import Interval
from app.models.stats import TopicStats


class Topic(BaseModel):
    """Full topic representation stored in Redis."""

    topic_id: str
    topic_name: str
    admin_name: str
    description: str | None = None
    constraints: list[Interval] = Field(default_factory=list)
    votes: dict[str, list[Interval]] = Field(default_factory=dict)
    created_at: datetime
    ttl_days: int


class TopicCreate(BaseModel):
    """Payload submitted by admin when creating a topic."""

    topic_name: str
    description: str | None = None
    constraints: list[Interval] = Field(default_factory=list)


class VotePayload(BaseModel):
    """Payload with the caller's full list of preferred intervals."""

    intervals: list[Interval] = Field(default_factory=list)


class ConstraintsPayload(BaseModel):
    """Payload used by admin to overwrite constraint windows."""

    constraints: list[Interval] = Field(default_factory=list)


class CreatedTopic(BaseModel):
    """Response after topic creation with link for sharing."""

    invite_link: str
    topic: Topic


class TopicResponse(BaseModel):
    """Bundle returned by GET/PUT endpoints with stats."""

    topic: Topic
    stats: TopicStats
