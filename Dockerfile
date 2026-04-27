FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip

COPY pyproject.toml .
COPY src/ src/
COPY cli/ cli/
COPY config/ config/

RUN pip install --no-cache-dir -e .

RUN mkdir -p data/db data/tokens data/logs

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "src.jarvis.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
