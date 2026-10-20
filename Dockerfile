# Base image with Python 3.14
FROM python:3.14-slim

# Install uv directly via official 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

# --frozen to strictly check uv.lock
RUN uv sync --frozen --no-install-project --no-dev