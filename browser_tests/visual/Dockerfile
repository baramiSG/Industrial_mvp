FROM mcr.microsoft.com/playwright/python:v1.62.0-noble@sha256:aa81288e738725378becba5b3e06cb0f3a7f012a610e87e8d767a090ea3f740d

ARG UV_VERSION=0.12.9
RUN python -m pip install --no-cache-dir "uv==${UV_VERSION}"

WORKDIR /workspace
COPY pyproject.toml uv.lock README.md ./
RUN UV_PROJECT_ENVIRONMENT=/opt/ior-venv \
    uv sync --locked --extra dev --extra e2e \
    --no-install-project --python "3.12"

ENV PATH="/opt/ior-venv/bin:${PATH}" \
    PLAYWRIGHT_BROWSERS_PATH="/ms-playwright" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1"
