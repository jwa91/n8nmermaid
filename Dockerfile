# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.13-slim
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.9.18

FROM ${UV_IMAGE} AS uv-bin

FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:${PATH}"

COPY --from=uv-bin /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY ./src /app/src

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uvicorn", "n8nmermaid.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
