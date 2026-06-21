FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
ENV PYTHONPATH=/app
ENV JARVIS_ENV=production
ENV JARVIS_DATABASE_URL=postgresql+asyncpg://jarvis:jarvis@postgres:5432/jarvis

EXPOSE 8000

CMD ["uvicorn", "jarvis.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
