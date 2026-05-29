import logging

from fastapi import APIRouter, Depends, HTTPException

from src.domain.entities import HealthResponse, ModelInfo, PredictRequest, PredictResponse
from src.infrastructure.model_loader import ModelLoader
from src.services.prediction_service import PredictionService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_service(loader: ModelLoader = Depends()) -> PredictionService:  # type: ignore[assignment]
    return PredictionService(loader)


@router.post("/predict", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    service: PredictionService = Depends(get_service),
) -> PredictResponse:
    try:
        return service.predict(req)
    except Exception as exc:
        logger.error("Ошибка предсказания: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/health", response_model=HealthResponse)
def health(loader: ModelLoader = Depends()) -> HealthResponse:  # type: ignore[assignment]
    return HealthResponse(status="ok", model_loaded=loader.is_loaded)


@router.get("/model-info", response_model=ModelInfo)
def model_info(loader: ModelLoader = Depends()) -> ModelInfo:  # type: ignore[assignment]
    return ModelInfo(
        name="NPCMoodClassifier",
        version="1.0.0",
        description="RandomForest предсказывает настроение NPC по контексту игры.",
        features=["game_hour", "player_gold", "player_hp", "npc_role_id", "npc_busy"],
        output_classes=loader.moods,
    )