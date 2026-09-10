FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

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

ENV PORT=8080
EXPOSE 8080
CMD ["./start.sh"]
