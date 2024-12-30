# Verwende das offizielle Python 3.11 Alpine Image als Basis
FROM python:3.11-alpine

# Installiere FFmpeg und andere benötigte Pakete
RUN apk add --no-cache ffmpeg

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere deine Anwendung ins Image
COPY . .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Definiere den Befehl zum Starten der Anwendung
CMD ["python", "main.py"]
