from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from math import ceil
from typing import Final

from app.core import config
from app.models import Interval, StatsInterval, Topic, TopicStats

SLOT = timedelta(minutes=config.GRID.SLOT_MINUTES_SIZE)
RATIO_CONFIG: Final[list[tuple[float, str]]] = [
    (0.9, "blocks_90"),
    (0.7, "blocks_70"),
    (0.5, "blocks_50"),
]


def build_topic_stats(topic: Topic) -> TopicStats:
    """Returns TopicStats with mutually exclusive percentile ladders."""
    bucket_counts = _count_buckets(topic.constraints, topic.votes.values())
    max_people = max(bucket_counts.values(), default=0)
    if max_people == 0:
        return TopicStats()

    ratios = [c[0] for c in RATIO_CONFIG]
    people_ranges = _compute_people_ranges(max_people, ratios)
    slot_labels = _classify_slots_by_ratio(bucket_counts, people_ranges)

    blocks: dict[str, list[StatsInterval]] = {}
    for ratio, field in RATIO_CONFIG:
        blocks[field] = _build_blocks(
            bucket_counts,
            slot_labels,
            ratio,
            people_ranges.get(ratio, (0, 0)),
        )
    return TopicStats(**blocks)


def _count_buckets(
    constraints: Iterable[Interval], votes: Iterable[list[Interval]]
) -> dict[datetime, int]:
    """Counts how many voters cover each allowed 15-minute bucket."""
    if not constraints:
        counts: dict[datetime, int] = {}
        for user_intervals in votes:
            for slot in _to_slots(user_intervals):
                counts[slot] = counts.get(slot, 0) + 1
        return counts

    allowed_slots = _to_slots(constraints)
    counts = {slot: 0 for slot in allowed_slots}
    for user_intervals in votes:
        for slot in allowed_slots:
            slot_end = slot + SLOT
            if any(
                interval.start <= slot and interval.end >= slot_end
                for interval in user_intervals
            ):
                counts[slot] += 1
    return counts


def _to_slots(intervals: Iterable[Interval]) -> list[datetime]:
    """Expands intervals into sorted bucket start times."""
    slots: set[datetime] = set()
    for window in intervals:
        slot_start = _ceil_to_slot(window.start)
        while slot_start + SLOT <= window.end:
            slots.add(slot_start)
            slot_start += SLOT
    return sorted(slots)


def _ceil_to_slot(moment: datetime) -> datetime:
    """Rounds a timestamp up to the next bucket boundary."""
    trimmed = moment.replace(second=0, microsecond=0)
    remainder = trimmed.minute % 15
    if remainder == 0 and moment.second == 0 and moment.microsecond == 0:
        return trimmed
    delta_minutes = (15 - remainder) % 15
    if delta_minutes == 0:
        delta_minutes = 15
    return trimmed + timedelta(minutes=delta_minutes)


def _compute_people_ranges(
    max_people: int, ratios: Iterable[float]
) -> dict[float, tuple[int, int]]:
    """Returns inclusive count ranges (e.g. [5,6]) for every ratio."""
    ranges: dict[float, tuple[int, int]] = {}
    upper_bound = max_people
    for ratio in sorted(ratios, reverse=True):
        lower_bound = max(1, ceil(max_people * ratio))
        if upper_bound < lower_bound:
            ranges[ratio] = (0, 0)
            continue
        ranges[ratio] = (lower_bound, upper_bound)
        upper_bound = lower_bound - 1
    return ranges


def _classify_slots_by_ratio(
    bucket_counts: dict[datetime, int],
    people_ranges: dict[float, tuple[int, int]],
) -> dict[datetime, float | None]:
    """Assigns each bucket to the highest ratio whose range contains it."""
    labels: dict[datetime, float | None] = {}
    ordered = sorted(people_ranges.keys(), reverse=True)
    for slot, count in bucket_counts.items():
        labels[slot] = None
        for ratio in ordered:
            lower, upper = people_ranges.get(ratio, (0, 0))
            if lower == upper == 0:
                continue
            if lower <= count <= upper:
                labels[slot] = ratio
                break
    return labels


def _build_blocks(
    bucket_counts: dict[datetime, int],
    slot_labels: dict[datetime, float | None],
    ratio: float,
    people_range: tuple[int, int],
) -> list[StatsInterval]:
    """Merges consecutive buckets already tagged with the target ratio."""
    if people_range == (0, 0):
        return []
    slots = sorted(bucket_counts)
    blocks: list[StatsInterval] = []
    current_start: datetime | None = None
    current_min: int | None = None
    current_max: int | None = None
    current_end: datetime | None = None

    for slot in slots:
        # Close the current block when there is a gap to keep intervals disjoint.
        if (
            current_start is not None
            and current_end is not None
            and slot != current_end + SLOT
        ):
            blocks.append(
                StatsInterval(
                    start=current_start,
                    end=(current_end or current_start) + SLOT,
                    people_min=current_min or people_range[0],
                    people_max=current_max or people_range[1],
                )
            )
            current_start = None
            current_min = current_max = None
            current_end = None

        if slot_labels.get(slot) != ratio:
            if current_start is None:
                continue
            blocks.append(
                StatsInterval(
                    start=current_start,
                    end=(current_end or current_start) + SLOT,
                    people_min=current_min or people_range[0],
                    people_max=current_max or people_range[1],
                )
            )
            current_start = None
            current_min = current_max = None
            current_end = None
            continue

        count = bucket_counts[slot]
        if current_start is None:
            current_start = slot
            current_min = current_max = count
            current_end = slot
            continue
        current_min = min(current_min or count, count)
        current_max = max(current_max or count, count)
        current_end = slot

    if current_start is not None:
        blocks.append(
            StatsInterval(
                start=current_start,
                end=(current_end or current_start) + SLOT,
                people_min=current_min or people_range[0],
                people_max=current_max or people_range[1],
            )
        )
    return blocks
