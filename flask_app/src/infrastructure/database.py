import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)
_SessionFactory: sessionmaker[Session] | None = None


def init_engine(database_url: str) -> None:
    global _SessionFactory
    engine = create_engine(database_url, pool_pre_ping=True)
    _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    logger.info("БД подключена.")


def get_session() -> Generator[Session, None, None]:
    assert _SessionFactory is not None, "init_engine не вызван"
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()