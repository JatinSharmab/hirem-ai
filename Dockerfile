FROM ghcr.io/astral-sh/uv:0.12.22 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONDONTWRITEBYTECODE=1
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev
COPY apps ./apps
COPY .streamlit/config.toml ./.streamlit/config.toml
COPY config ./config
COPY data/demo ./data/demo
COPY migrations ./migrations
COPY scripts ./scripts
COPY alembic.ini ./
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uv", "run", "--no-sync", "python", "scripts/serve_api.py"]
