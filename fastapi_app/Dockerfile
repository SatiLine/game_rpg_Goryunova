FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY fastapi_app/pyproject.toml .
RUN uv sync --no-dev

COPY fastapi_app/src/ src/

# Создаём папку для модели (она будет пустой, если модели нет)
RUN mkdir -p models

# Копируем скрипт обучения из корневой папки ml/
COPY ml/train.py /tmp/train.py

# Обучаем модель, если её ещё нет
RUN if [ ! -f models/npc_model.pkl ]; then \
        uv run python /tmp/train.py models/npc_model.pkl; \
    fi

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]