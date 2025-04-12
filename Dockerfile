FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    torch \
    transformers \
    accelerate \
    text-generation-launcher \
    huggingface_hub

RUN mkdir -p /app/model

ENV MODEL_ID="phanerozoic/Tiny-Viking-1.1b-v0.1"
ENV HF_HOME=/app/model

COPY download_model.py .

CMD ["text-generation-launcher", "--model-id", "phanerozoic/Tiny-Viking-1.1b-v0.1", "--port", "8080", "--host", "0.0.0.0"]