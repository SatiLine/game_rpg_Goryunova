FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv sync --no-dev

COPY src/ src/
COPY models/ models/ 2>/dev/null || true

# обучаем модель если её ещё нет
COPY ../ml/train.py /tmp/train.py
RUN if [ ! -f models/npc_model.pkl ]; then \
        uv run python /tmp/train.py models/npc_model.pkl; \
    fi

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]