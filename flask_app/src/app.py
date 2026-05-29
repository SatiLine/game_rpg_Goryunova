import logging

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from src.config import config
from src.game.npc_manager import NPCManager
from src.game.world import World
from src.infrastructure.database import get_session, init_engine
from src.infrastructure.repositories import PredictionRepository, UserRepository
from src.services.auth_service import AuthService
from src.services.game_service import GameService
from src.web.auth_bp import auth_bp
from src.web.game_bp import game_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)
csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = config.secret_key
    app.config["SQLALCHEMY_DATABASE_URI"] = config.database_url
    app.config["WTF_CSRF_ENABLED"] = True

    csrf.init_app(app)
    init_engine(config.database_url)

    # создаём общие объекты игрового мира
    world = World()
    npc_manager = NPCManager("src/game/data/npcs.json")

    app.extensions["world"] = world
    app.extensions["npc_manager"] = npc_manager

    # DI: сервисы с зависимостями через конструктор
    # сессию открываем на каждый запрос через before_request
    @app.before_request
    def _attach_services() -> None:
        from flask import g

        session_gen = get_session()
        g.db = next(session_gen)
        g._session_gen = session_gen
        g.auth_service = AuthService(UserRepository(g.db))
        g.game_service = GameService(PredictionRepository(g.db), config.ml_api_url)
        app.extensions["auth_service"] = g.auth_service
        app.extensions["game_service"] = g.game_service

    @app.teardown_request
    def _close_session(exc: BaseException | None) -> None:
        from flask import g

        gen = getattr(g, "_session_gen", None)
        if gen is not None:
            try:
                next(gen)
            except StopIteration:
                pass

    app.register_blueprint(auth_bp)
    app.register_blueprint(game_bp)

    logger.info("Flask приложение создано.")
    return app
