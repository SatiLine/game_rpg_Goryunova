import logging
import random

import requests

from src.config import settings
from src.domain.entities import PredictRequest, PredictResponse
from src.infrastructure.model_loader import ModelLoader

logger = logging.getLogger(__name__)

# шаблоны диалога по роли и настроению (fallback без Ollama)
_TEMPLATES: dict[tuple[str, str], list[str]] = {
    ("кузнец", "friendly"):  ["Добрый день, путник! Могу что-то сковать для тебя.", "Хорошо выглядишь. Нужна броня?"],
    ("кузнец", "neutral"):   ["Чего тебе? Говори быстрее, работы много.", "Ну?"],
    ("кузнец", "hostile"):   ["Убирайся, не мешай!", "Не в настроении я сегодня."],
    ("кузнец", "busy"):      ["Не видишь — занят! Позже.", "Стучи позже."],
    ("трактирщица", "friendly"):  ["Добро пожаловать! Что будешь — эль или похлёбку?", "Рада тебя видеть, странник!"],
    ("трактирщица", "neutral"):   ["Чего желаешь?", "Слушаю тебя."],
    ("трактирщица", "hostile"):   ["Ты мне не нравишься. Деньги вперёд.", "Смотри у меня."],
    ("трактирщица", "busy"):      ["Минуту, много клиентов сегодня.", "Подожди чуть-чуть."],
    ("торговец", "friendly"):     ["О, покупатель! У меня лучший товар в городе!", "Для тебя — особая цена."],
    ("торговец", "neutral"):      ["Смотри, не трогай руками.", "Чем могу?"],
    ("торговец", "hostile"):      ["Нечего тут смотреть без денег.", "Уходи, если не покупаешь."],
    ("торговец", "busy"):         ["Сейчас занят подсчётом. Позже.", "Не мешай."],
}
_DEFAULT = {
    "friendly": ["Рад тебя видеть.", "Привет, странник!"],
    "neutral":  ["Да?", "Чего тебе?"],
    "hostile":  ["Уйди.", "Не до тебя."],
    "busy":     ["Занят.", "Позже."],
}


def _template_dialogue(npc_role: str, mood: str) -> str:
    lines = _TEMPLATES.get((npc_role, mood), _DEFAULT.get(mood, ["..."]))
    return random.choice(lines)


def _ollama_dialogue(req: PredictRequest, mood: str) -> str | None:
    if not settings.ollama_url:
        return None

    ltm = "; ".join(req.npc_long_term_memory) or "ничего особенного"
    system = (
        f"Ты — {req.npc_name}, {req.npc_role} в средневековом городе.\n"
        f"Характер: {req.npc_personality}\n"
        f"О себе: {ltm}\n"
        f"Сейчас {req.game_hour:02d}:00, ты {req.npc_state}, твоё настроение: {mood}.\n"
        f"Разговариваешь с {req.player_name}.\n"
        "Отвечай коротко (1-2 предложения) на русском, строго в образе. Не упоминай что ты ИИ."
    )

    # история + новое сообщение
    messages = list(req.conversation_history) + [
        {"role": "user", "content": req.player_message}
    ]

    try:
        r = requests.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model":   settings.ollama_model,
                "stream":  False,
                "options": {"num_predict": 100, "temperature": 0.8},
                "messages": [{"role": "system", "content": system}] + messages,
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except requests.Timeout:
        logger.error("Ollama таймаут для %s", req.npc_id)
        return None
    except Exception as exc:
        logger.error("Ollama ошибка: %s", exc)
        return None


class PredictionService:
    def __init__(self, loader: ModelLoader) -> None:
        self._loader = loader

    def predict(self, req: PredictRequest) -> PredictResponse:
        mood, confidence = self._loader.predict(
            game_hour=req.game_hour,
            player_gold=req.player_gold,
            player_hp=req.player_hp,
            npc_role=req.npc_role,
            npc_state=req.npc_state,
        )
        logger.info("NPC %s: mood=%s (%.2f)", req.npc_id, mood, confidence)

        dialogue = _ollama_dialogue(req, mood) or _template_dialogue(req.npc_role, mood)

        return PredictResponse(
            npc_id=req.npc_id,
            npc_mood=mood,
            mood_confidence=round(confidence, 3),
            dialogue=dialogue,
        )