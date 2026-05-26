"""Скрипт обучения модели предсказания настроения NPC."""

import logging
import os
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

NPC_ROLES = ["кузнец", "трактирщица", "торговец", "стражник", "маг"]
MOODS = ["hostile", "neutral", "friendly", "busy"]

ROLE_ENC = LabelEncoder().fit(NPC_ROLES)
STATE_ENC = LabelEncoder().fit(["idle", "working", "sleeping", "wandering"])


def generate_data(n: int = 3000) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)

    game_hour   = rng.integers(0, 24, n)
    player_gold = rng.integers(0, 200, n)
    player_hp   = rng.integers(10, 100, n)
    npc_role_id = rng.integers(0, len(NPC_ROLES), n)
    npc_busy    = rng.integers(0, 2, n)  # 1 = working/wandering

    X = np.column_stack([game_hour, player_gold, player_hp, npc_role_id, npc_busy])

    # правила для генерации меток
    mood = np.full(n, 1, dtype=int)  # neutral по умолчанию
    mood[npc_busy == 1] = 3                            # busy
    mood[(player_gold > 100) & (npc_busy == 0)] = 2   # friendly
    mood[(player_hp < 30) & (npc_role_id == 3)] = 0   # hostile (стражник видит слабого)
    noise_idx = rng.choice(n, size=n // 10, replace=False)
    mood[noise_idx] = rng.integers(0, 4, len(noise_idx))

    return X, mood


def train(output_path: Path) -> None:
    logger.info("Генерация обучающих данных...")
    X, y = generate_data(5000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logger.info("Обучение RandomForestClassifier...")
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    acc = clf.score(X_test, y_test)
    logger.info("Точность на тесте: %.3f", acc)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": clf, "moods": MOODS}, output_path)
    logger.info("Модель сохранена: %s", output_path)


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("fastapi_app/models/npc_model.pkl")
    train(path)