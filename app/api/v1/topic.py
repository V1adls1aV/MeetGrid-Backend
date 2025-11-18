from __future__ import annotations

from fastapi import APIRouter, status

from app.models import (
    ConstraintsPayload,
    CreatedTopic,
    TopicCreate,
    TopicResponse,
    VotePayload,
)
from app.service import (
    build_invite_link,
    create_topic,
    get_topic_with_stats,
    overwrite_constraints,
    replace_vote,
)

router = APIRouter(prefix="/topic", tags=["Topics"])


@router.post("", response_model=CreatedTopic, status_code=status.HTTP_201_CREATED)
async def create_topic_v1(username: str, payload: TopicCreate) -> CreatedTopic:
    """Creates a topic record and returns invite link."""
    topic = await create_topic(username, payload)
    return CreatedTopic(invite_link=build_invite_link(topic.topic_id), topic=topic)


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic_v1(topic_id: str, username: str | None = None) -> TopicResponse:
    """Returns topic with stats; username kept for parity with frontend API."""
    topic, stats = await get_topic_with_stats(topic_id)
    return TopicResponse(topic=topic, stats=stats)


@router.put("/{topic_id}/pick", response_model=TopicResponse)
async def pick_intervals_v1(
    topic_id: str, username: str, payload: VotePayload
) -> TopicResponse:
    """Saves caller vote and returns latest topic snapshot."""
    topic, stats = await replace_vote(topic_id, username, payload)
    return TopicResponse(topic=topic, stats=stats)


@router.put("/{topic_id}/constraints", response_model=TopicResponse)
async def update_constraints_v1(
    topic_id: str, username: str, payload: ConstraintsPayload
) -> TopicResponse:
    """Allows admin to overwrite constraint windows."""
    topic, stats = await overwrite_constraints(topic_id, username, payload)
    return TopicResponse(topic=topic, stats=stats)
