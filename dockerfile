FROM python:3.13.3-slim

# Installa dipendenze di sistema per MoviePy e video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Imposta directory di lavoro
WORKDIR /app

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice sorgente
COPY . .

# Aggiungi /app al PYTHONPATH per trovare i moduli
ENV PYTHONPATH=/app

# Comando di default (viene sovrascritto nel docker-compose)
CMD ["celery", "-A", "Video_clip", "worker", "--loglevel=info"]