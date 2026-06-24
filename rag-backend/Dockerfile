FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
RUN uv sync --no-group dev --frozen 2>/dev/null || uv sync --no-group dev

COPY . .

EXPOSE 8000
CMD [".venv/bin/python", "main.py"]
