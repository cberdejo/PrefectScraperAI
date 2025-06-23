FROM python:3.11-slim as base

# Instalar dependencias del sistema necesarias para uv y librerías Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar uv
FROM base AS uv-installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"


FROM uv-installer AS setup
WORKDIR /app
COPY . .
RUN uv venv .venv
RUN uv sync



