FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

RUN pip install uv

WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./
COPY ./src /app/src

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "--", "uvicorn", "src.n8nmermaid.api.main:app", "--host", "0.0.0.0", "--port", "8000"]