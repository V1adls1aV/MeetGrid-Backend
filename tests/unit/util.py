from __future__ import annotations

from datetime import datetime, timedelta

from app.models import Interval, Topic


def topic(constraints: list[Interval], votes: dict[str, list[Interval]]) -> Topic:
    return Topic(
        topic_id="tid",
        topic_name="Demo",
        admin_name="Admin",
        description=None,
        constraints=constraints,
        votes=votes,
        created_at=datetime(2025, 1, 1, 8, 0),
    )


def make_interval(
    base: datetime, minutes: tuple[int, int] = (0, 0), hours: tuple[int, int] = (0, 0)
) -> Interval:
    return Interval(
        start=base + timedelta(minutes=minutes[0], hours=hours[0]),
        end=base + timedelta(minutes=minutes[1], hours=hours[1]),
    )


def make_simple_tuple(
    base: datetime, minutes: tuple[int, int] = (0, 0), hours: tuple[int, int] = (0, 0)
) -> tuple[datetime, datetime]:
    return (
        base + timedelta(minutes=minutes[0], hours=hours[0]),
        base + timedelta(minutes=minutes[1], hours=hours[1]),
    )


def simplify(blocks: list) -> list[tuple[datetime, datetime]]:
    return [(block.start, block.end) for block in blocks]
