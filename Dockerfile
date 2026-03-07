FROM python:3.11-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# System deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install deps first (for layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy source & install the project itself
COPY config/ config/
COPY src/ src/
COPY README.md ./
RUN uv sync --frozen --no-dev

# Prevent uv run from trying to sync at runtime
ENV UV_NO_SYNC=1

# Non-root user
RUN useradd --create-home appuser
USER appuser

ENTRYPOINT ["uv", "run", "paperfinder"]
CMD ["serve"]
