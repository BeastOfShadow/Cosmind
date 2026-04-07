# Usa un'immagine Python leggera e aggiornata
FROM python:3.11-slim

# Evita di scrivere .pyc e forza print su console
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copia e installa le dipendenze
COPY requirements.txt .

# Installa pacchetti di sistema se necessari per la compilazione (Chromadb talvolta richiede tools gcc/g++)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice del progetto nel container
COPY . /app

# Comando per mantenere il container vivo o lanciare uno script preciso
CMD ["bash"]