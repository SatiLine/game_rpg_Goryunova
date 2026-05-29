import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    from src.main import app
    with patch("src.infrastructure.model_loader.ModelLoader.load"):
        with patch("src.infrastructure.model_loader.ModelLoader.predict", return_value=("neutral", 0.8)):
            with patch("src.infrastructure.model_loader.ModelLoader.is_loaded", True):
                with patch("src.infrastructure.model_loader.ModelLoader.moods", ["hostile","neutral","friendly","busy"]):
                    yield TestClient(app)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_model_info(client: TestClient) -> None:
    r = client.get("/model-info")
    assert r.status_code == 200
    data = r.json()
    assert "name" in data
    assert "features" in data


def test_predict(client: TestClient) -> None:
    r = client.post("/predict", json={
        "npc_id": "blacksmith_oren",
        "npc_name": "Орен",
        "npc_role": "кузнец",
        "npc_personality": "Грубоватый",
        "npc_state": "working",
        "game_hour": 14,
        "player_name": "Странник",
        "player_hp": 80,
        "player_gold": 30,
        "player_message": "Привет",
    })
    assert r.status_code == 200
    data = r.json()
    assert "dialogue" in data
    assert "npc_mood" in data