FROM python:3.13-slim

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY api/ ./api/
COPY services/ ./services/
COPY resources/ ./resources/

EXPOSE 8080

CMD ["uv", "run", "python", "api/main.py"]
