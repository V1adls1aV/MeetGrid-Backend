import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as client:
        yield client
