FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY producer/pyproject.toml producer/uv.lock ./producer/
RUN cd producer && uv sync --locked --no-dev

COPY producer/src ./producer/src

WORKDIR /app/producer

CMD ["uv", "run", "python", "-m", "main"]
