FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/docker_app.py src/docker_app.py

ENV MODEL_ID="phanerozoic/Tiny-Viking-1.1b-v0.1"
ENV HF_HOME=/app/cache

CMD ["uvicorn", "src.docker_app:app", "--host", "0.0.0.0", "--port", "8080"]