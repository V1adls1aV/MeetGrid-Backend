from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from app.models import (
    ConstraintsPayload,
    CreatedTopic,
    TopicCreate,
    TopicResponse,
    VotePayload,
)

router = APIRouter(prefix="/topic", tags=["Topics"])


@router.post("", response_model=CreatedTopic, status_code=status.HTTP_201_CREATED)
def create_topic_v1(
    username: str, payload: TopicCreate
) -> CreatedTopic:  # pragma: no cover - stub
    """Creates a topic; actual persistence will be wired later."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic_v1(
    topic_id: str, username: str | None = None
) -> TopicResponse:  # pragma: no cover - stub
    """Returns topic info with stats once storage is ready."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{topic_id}/pick", response_model=TopicResponse)
def pick_intervals_v1(
    topic_id: str, username: str, payload: VotePayload
) -> TopicResponse:  # pragma: no cover - stub
    """Saves the caller vote and returns latest topic snapshot."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.put("/{topic_id}/constraints", response_model=TopicResponse)
def update_constraints_v1(
    topic_id: str, username: str, payload: ConstraintsPayload
) -> TopicResponse:  # pragma: no cover - stub
    """Allows admin to overwrite constraint windows."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
