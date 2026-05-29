import logging
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

NPC_ROLES = ["кузнец", "трактирщица", "торговец", "стражник", "маг"]
NPC_STATES = ["idle", "working", "sleeping", "wandering"]


class ModelLoader:
    def __init__(self, model_path: str) -> None:
        self._path = Path(model_path)
        self._model: Any = None
        self._moods: list[str] = []
        self._loaded = False

    def load(self) -> None:
        try:
            data = joblib.load(self._path)
            self._model = data["model"]
            self._moods = data["moods"]
            self._loaded = True
            logger.info("Модель загружена из %s", self._path)
        except Exception as exc:
            logger.error("Ошибка загрузки модели: %s", exc)
            raise

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def moods(self) -> list[str]:
        return self._moods

    def predict(
        self,
        game_hour: int,
        player_gold: int,
        player_hp: int,
        npc_role: str,
        npc_state: str,
    ) -> tuple[str, float]:
        role_id = NPC_ROLES.index(npc_role) if npc_role in NPC_ROLES else 2
        busy = 1 if npc_state in ("working", "wandering") else 0

        X = np.array([[game_hour, player_gold, player_hp, role_id, busy]])
        idx = int(self._model.predict(X)[0])
        proba = float(self._model.predict_proba(X)[0][idx])
        return self._moods[idx], proba
