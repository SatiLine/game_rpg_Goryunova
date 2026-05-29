import logging

from fastapi import FastAPI

from src.api.routes import router
from src.config import settings
from src.infrastructure.model_loader import ModelLoader

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

_loader = ModelLoader(settings.model_path)


def create_app() -> FastAPI:
    application = FastAPI(title="RPG ML API", version="1.0.0")
    application.include_router(router)

    @application.on_event("startup")
    def startup() -> None:
        _loader.load()
        logger.info("FastAPI запущен, модель готова.")

    application.state.loader = _loader
    return application


app = create_app()