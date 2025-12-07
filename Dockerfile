FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN uv sync --frozen --no-dev


ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Only one uvicorn worker here to let k8s handle the scaling
CMD ["uvicorn", "hivebox.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
