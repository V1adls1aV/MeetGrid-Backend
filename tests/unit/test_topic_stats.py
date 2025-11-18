from __future__ import annotations
from functools import partial
from datetime import datetime

from app.models import Interval
from app.services import build_topic_stats
from tests.unit.util import topic, make_interval, make_simple_tuple, simplify


def test_returns_empty_stats_without_constraints() -> None:
    stats = build_topic_stats(topic([], {}))
    assert stats.blocks_90 == []
    assert stats.blocks_70 == []
    assert stats.blocks_50 == []


def test_each_slot_picks_only_one_ratio() -> None:
    base = datetime(2025, 1, 1, 8, 0)
    get_interval = partial(make_interval, base)
    get_tuple_interval = partial(make_simple_tuple, base)
    constraints = [get_interval((0, 90))]
    votes = {
        "a": [get_interval((0, 60))],
        "b": [get_interval((0, 60))],
        "c": [get_interval((0, 60))],
        "d": [get_interval((15, 75))],
        "e": [get_interval((30, 90))],
        "f": [get_interval((30, 90))],
    }
    stats = build_topic_stats(topic(constraints, votes))

    assert simplify(stats.blocks_90) == [get_tuple_interval((30, 60))]
    assert stats.blocks_70 == []
    assert simplify(stats.blocks_50) == [
        get_tuple_interval((0, 30)),
        get_tuple_interval((60, 75)),
    ]
    first_block, second_block = stats.blocks_50
    assert (first_block.people_min, first_block.people_max) == (3, 4)
    assert (second_block.people_min, second_block.people_max) == (3, 3)


def test_percentile_blocks_are_mutually_exclusive() -> None:
    base = datetime(2025, 1, 1, 9, 0)
    get_interval = partial(make_interval, base)
    get_tuple_interval = partial(make_simple_tuple, base)
    constraints = [get_interval((0, 420))]
    votes: dict[str, list[Interval]] = {}

    for idx in range(5):
        votes[f"core{idx}"] = [get_interval((0, 420))]
    votes["extra50"] = [get_interval((0, 360))]
    for idx in range(2):
        votes[f"seventy{idx}"] = [get_interval((120, 360))]
    for idx in range(2):
        votes[f"ninety{idx}"] = [get_interval((180, 360))]

    stats = build_topic_stats(topic(constraints, votes))

    assert simplify(stats.blocks_90) == [get_tuple_interval(hours=(3, 6))]
    assert [block.people_min for block in stats.blocks_90] == [10]

    assert simplify(stats.blocks_70) == [get_tuple_interval(hours=(2, 3))]
    assert [block.people_min for block in stats.blocks_70] == [8]

    assert simplify(stats.blocks_50) == [
        get_tuple_interval(hours=(0, 2)),
        get_tuple_interval(hours=(6, 7)),
    ]
    mins = [(block.people_min, block.people_max) for block in stats.blocks_50]
    assert mins == [(6, 6), (5, 5)]


def test_day_sections_get_independent_percentiles() -> None:
    morning_base = datetime(2025, 1, 2, 9, 0)
    evening_base = datetime(2025, 1, 2, 16, 0)
    morning = partial(make_interval, morning_base)
    evening = partial(make_interval, evening_base)

    constraints = [morning((0, 180)), evening((0, 240))]
    votes: dict[str, list[Interval]] = {}

    for idx in range(5):
        votes[f"core{idx}"] = [morning((0, 180)), evening((0, 240))]
    votes["fifty"] = [morning((0, 180)), evening((0, 180))]
    votes["seventy"] = [morning((60, 180)), evening((60, 180))]
    votes["morning90a"] = [morning((120, 180))]
    votes["morning90b"] = [morning((120, 180))]
    votes["evening90a"] = [evening((120, 180))]
    votes["evening90b"] = [evening((120, 180))]

    stats = build_topic_stats(topic(constraints, votes))

    assert simplify(stats.blocks_90) == [
        (datetime(2025, 1, 2, 11), datetime(2025, 1, 2, 12)),
        (datetime(2025, 1, 2, 18), datetime(2025, 1, 2, 19)),
    ]
    assert simplify(stats.blocks_70) == [
        (datetime(2025, 1, 2, 10), datetime(2025, 1, 2, 11)),
        (datetime(2025, 1, 2, 17), datetime(2025, 1, 2, 18)),
    ]
    assert simplify(stats.blocks_50) == [
        (datetime(2025, 1, 2, 9), datetime(2025, 1, 2, 10)),
        (datetime(2025, 1, 2, 16), datetime(2025, 1, 2, 17)),
        (datetime(2025, 1, 2, 19), datetime(2025, 1, 2, 20)),
    ]


def test_constraint_edges_are_respected() -> None:
    base = datetime(2025, 1, 1, 10, 5)
    get_interval = partial(make_interval, base)
    constraints = [get_interval((0, 45))]
    votes = {"solo": [get_interval((0, 45))]}
    stats = build_topic_stats(topic(constraints, votes))

    assert simplify(stats.blocks_90) == [
        (datetime(2025, 1, 1, 10, 15), datetime(2025, 1, 1, 10, 45))
    ]
    assert simplify(stats.blocks_70) == []
    assert simplify(stats.blocks_50) == []
