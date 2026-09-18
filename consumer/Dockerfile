FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY consumer/pyproject.toml consumer/uv.lock ./consumer/
RUN cd consumer && uv sync --locked --no-dev

COPY consumer/src ./consumer/src

WORKDIR /app/consumer

ENV PATH="/app/consumer/.venv/bin:$PATH"

CMD ["python", "src/main.py"]
