FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY plex_refresher/ /app/plex_refresher/
COPY main.py .

RUN mkdir -p /app/data/logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Use tini as init system to handle signals properly
RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "main.py"]