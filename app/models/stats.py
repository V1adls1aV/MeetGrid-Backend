from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StatsInterval(BaseModel):
    """Represents a merged 15-minute block for ladder cards."""

    start: datetime
    end: datetime
    people_min: int = Field(ge=0)
    people_max: int = Field(ge=0)


class TopicStats(BaseModel):
    """Stores precomputed availability ladders for a topic."""

    blocks_90: list[StatsInterval] = Field(default_factory=list)
    blocks_70: list[StatsInterval] = Field(default_factory=list)
    blocks_50: list[StatsInterval] = Field(default_factory=list)
