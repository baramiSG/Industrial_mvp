FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY config ./config
COPY data ./data
COPY docs ./docs
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "ior_mvp.app:app", "--host", "0.0.0.0", "--port", "8000"]
