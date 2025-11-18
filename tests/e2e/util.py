from datetime import datetime, timedelta

from fastapi.testclient import TestClient

BASE = datetime(2025, 1, 1, 9, 0)


def interval(minutes_start: int, minutes_end: int) -> dict[str, str]:
    return {
        "start": (BASE + timedelta(minutes=minutes_start)).isoformat(),
        "end": (BASE + timedelta(minutes=minutes_end)).isoformat(),
    }


def create_topic(client: TestClient) -> dict:
    payload = {
        "topic_name": "Sprint planning",
        "description": "Weekly sync",
        "constraints": [interval(0, 60)],
    }
    response = client.post("/api/v1/topic", params={"username": "alice"}, json=payload)
    assert response.status_code == 201
    return response.json()
