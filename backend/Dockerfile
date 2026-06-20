FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt build.sh ./
RUN chmod +x build.sh && ./build.sh

COPY . .

ENV PORT=8000
EXPOSE $PORT

CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
