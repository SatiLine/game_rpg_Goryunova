import logging

import requests

from src.domain.entities import Prediction
from src.domain.interfaces import PredictionRepositoryProtocol

logger = logging.getLogger(__name__)


class GameService:
    def __init__(
        self,
        prediction_repo: PredictionRepositoryProtocol,
        ml_api_url: str,
    ) -> None:
        self._repo = prediction_repo
        self._ml_url = ml_api_url

    def talk_to_npc(
        self,
        user_id: int,
        npc_data: dict[str, object],
        player_context: dict[str, object],
        player_message: str,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            **npc_data,
            **player_context,
            "player_message": player_message,
        }
        try:
            r = requests.post(
                f"{self._ml_url}/predict",
                json=payload,  # type: ignore[arg-type]
                timeout=30,
            )
            r.raise_for_status()
            result: dict[str, object] = r.json()
        except requests.Timeout:
            logger.error("ML API таймаут для NPC %s", npc_data.get("npc_id"))
            result = {
                "npc_id": npc_data.get("npc_id"),
                "dialogue": "...",
                "npc_mood": "unknown",
                "mood_confidence": 0.0,
            }
        except Exception as exc:
            logger.error("Ошибка ML API: %s", exc)
            result = {
                "npc_id": npc_data.get("npc_id"),
                "dialogue": "Хм.",
                "npc_mood": "unknown",
                "mood_confidence": 0.0,
            }

        self._repo.create(
            user_id=user_id,
            input_data=payload,
            prediction=result,
        )
        return result

    def get_history(self, user_id: int) -> list[Prediction]:
        return self._repo.get_by_user(user_id)
