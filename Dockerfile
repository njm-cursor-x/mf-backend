FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV MF_BOOT=entrypoint-v2

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY ingest ./ingest
COPY data ./data
COPY start.sh ./start.sh
RUN chmod +x start.sh

EXPOSE 8080
ENTRYPOINT ["python", "-m", "app.run"]
CMD []
