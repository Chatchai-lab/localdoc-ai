# 1. Basis: Ein schlankes Python-Image
FROM python:3.10-slim

# 2. System-Abhängigkeiten installieren (wichtig für PDF-Verarbeitung)
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic-dev \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3. Arbeitsverzeichnis festlegen
WORKDIR /app

# 4. Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# 4.1. Docling (PDF) Abhängigkeiten installieren (kann sehr lange dauern)
COPY requirements-pdf.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements-pdf.txt

# 5. Den restlichen Code kopieren (nur app/)
COPY backend/app/ ./app/

# 6. Ordner für Uploads und Datenbank erstellen (wenn nicht vorhanden)
RUN mkdir -p /app/data/documents /app/data/processed /app/data/vector_db /app/data/vector_db_docling

# 7. Port öffnen
EXPOSE 8000

# 8. Startbefehl
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]