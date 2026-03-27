FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fetch and ingest EU AI Act on build
RUN python -m app.services.fetch_eu_ai_act && python -c "import asyncio; from app.services.ingest_ai_act import ingest_eu_ai_act; asyncio.run(ingest_eu_ai_act())"

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
