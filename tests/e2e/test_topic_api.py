from __future__ import annotations

from fastapi.testclient import TestClient

from app.core import config

from .util import create_topic, interval


def test_create_topic_returns_invite_link(client: TestClient) -> None:
    created = create_topic(client)
    topic = created["topic"]
    assert (
        created["invite_link"]
        == f"{config.SITE_BASE_URL.rstrip('/')}/topic/{topic['topic_id']}"
    )
    assert topic["admin_name"] == "alice"
    assert topic["created_at"].endswith("+03:00")


def test_get_topic_returns_empty_stats(client: TestClient) -> None:
    created = create_topic(client)
    topic_id = created["topic"]["topic_id"]

    response = client.get(f"/api/v1/topic/{topic_id}")
    body = response.json()

    assert response.status_code == 200
    assert body["topic"]["topic_id"] == topic_id
    assert body["stats"] == {
        "blocks_90": [],
        "blocks_70": [],
        "blocks_50": [],
        "vote_count": 0,
    }


def test_pick_vote_updates_stats_for_multiple_users(client: TestClient) -> None:
    created = create_topic(client)
    topic_id = created["topic"]["topic_id"]

    response = client.put(
        f"/api/v1/topic/{topic_id}/pick",
        params={"username": "alice"},
        json={"intervals": [interval(0, 60)]},
    )
    assert response.status_code == 200
    first_stats = response.json()["stats"]
    assert first_stats["blocks_90"]

    response = client.put(
        f"/api/v1/topic/{topic_id}/pick",
        params={"username": "bob"},
        json={"intervals": [interval(30, 60)]},
    )
    stats = response.json()["stats"]

    assert stats["blocks_90"][0]["start"].endswith("09:30:00")
    assert stats["blocks_90"][0]["end"].endswith("10:00:00")
    assert stats["blocks_90"][0]["people_min"] == 2
    assert stats["blocks_50"][0]["people_min"] == 1


def test_double_pick_updates_stats_for_multiple_users(client: TestClient) -> None:
    created = create_topic(client)
    topic_id = created["topic"]["topic_id"]

    response = client.put(
        f"/api/v1/topic/{topic_id}/pick",
        params={"username": "alice"},
        json={"intervals": [interval(30, 45)]},
    )
    assert response.status_code == 200
    assert response.json()["stats"]["blocks_90"]

    response = client.put(
        f"/api/v1/topic/{topic_id}/pick",
        params={"username": "bob"},
        json={"intervals": [interval(30, 60)]},
    )

    response = client.put(
        f"/api/v1/topic/{topic_id}/pick",
        params={"username": "alice"},
        json={"intervals": [interval(0, 60)]},
    )
    stats = response.json()["stats"]

    assert stats["blocks_90"][0]["start"].endswith("09:30:00")
    assert stats["blocks_90"][0]["end"].endswith("10:00:00")
    assert stats["blocks_90"][0]["people_min"] == 2
    assert stats["blocks_50"][0]["people_min"] == 1


def test_update_constraints_requires_admin(client: TestClient) -> None:
    created = create_topic(client)
    topic_id = created["topic"]["topic_id"]
    payload = {"constraints": [interval(60, 120)]}

    forbidden = client.put(
        f"/api/v1/topic/{topic_id}/constraints",
        params={"username": "bob"},
        json=payload,
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"] == "Only topic admin can perform this action."

    allowed = client.put(
        f"/api/v1/topic/{topic_id}/constraints",
        params={"username": "alice"},
        json=payload,
    )
    assert allowed.status_code == 200
    topic = allowed.json()["topic"]
    assert topic["constraints"][0]["start"].endswith("10:00:00")


def test_nonexistent_topic_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/topic/nonexistent")
    assert response.status_code == 404


def test_interval_continuity(client: TestClient) -> None:
    created = create_topic(client)
    topic_id = created["topic"]["topic_id"]

    assert (
        client.put(
            f"/api/v1/topic/{topic_id}/pick",
            params={"username": "alice"},
            json={"intervals": [interval(0, 60)]},
        ).status_code
        == 200
    )

    assert (
        client.put(
            f"/api/v1/topic/{topic_id}/pick",
            params={"username": "bob"},
            json={"intervals": [interval(30, 60)]},
        ).status_code
        == 200
    )

    assert (
        client.put(
            f"/api/v1/topic/{topic_id}/pick",
            params={"username": "vlad"},
            json={"intervals": [interval(0, 30)]},
        ).status_code
        == 200
    )

    assert client.get(f"/api/v1/topic/{topic_id}").json()["stats"]["blocks_90"] == [
        {
            "start": "2025-01-01T09:00:00",
            "end": "2025-01-01T10:00:00",
            "people_min": 2,
            "people_max": 2,
        }
    ]
