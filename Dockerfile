FROM python:3.11-slim-bullseye

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install -r requirements.txt

ENV MODEL_PATH=/app/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
ENV SEARCH_API=""

CMD ["python", "app.py"]
