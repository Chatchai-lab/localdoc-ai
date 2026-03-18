# LocalDoc AI – Setup-Anleitung

Willkommen bei LocalDoc AI! Diese App ermöglicht es dir, PDFs lokal hochzuladen, zu verarbeiten und einer KI (über Ollama) Fragen zu diesen Dokumenten zu stellen. Alles läuft zu 100 % lokal und privat auf deinem PC.

## Voraussetzungen

Bevor du beginnst, stelle sicher, dass folgende Programme auf deinem System installiert sind:
* **Git** (um das Projekt herunterzuladen)
* **Docker** und **Docker Compose**
* **Ollama** (für das lokale KI-Sprachmodell)

## Installation & Start

### 1. Repository klonen
Lade dir den Code aus dem GitHub-Repository herunter und wechsle in den Projektordner:
```bash
git clone https://github.com/Chatchai-lab/localdoc-ai.git
cd localdoc-ai
```

### 2. Ollama & KI-Modell starten
Das Backend benötigt Ollama, um Antworten zu generieren. Starte Ollama und lade das Standard-Sprachmodell (`llama3.1`), welches in der App verwendet wird:
```bash
# Lade das KI-Modell herunter
ollama pull llama3.1

# Stelle sicher, dass Ollama im Hintergrund läuft
ollama serve
```

### 3. Mit Docker starten (Schnell & Einfach)
Du kannst das komplette System (Frontend, Backend, Datenbanken) mit nur einem Befehl über Docker starten. 

```bash
docker-compose up -d --build
```
*(Der Zusatz `-d` startet die Container im Hintergrund. Der erste Start kann einige Minuten dauern, da das Docker-Image gebaut und Abhängigkeiten heruntergeladen werden).*

Fertig! Öffne nun deinen Browser und besuche: **http://localhost:5173**

---

## Hinweis zu "Docling" (Erweiterte PDF-Verarbeitung)

Dieses Projekt nutzt einen intelligenten Fallback-Mechanismus für die Textverarbeitung. Es unterstützt **Docling**, ein leistungsstarkes Tool von IBM, das PDFs inklusive komplexer Tabellen in sauberes Markdown umwandeln kann.

Da Docling relativ groß ist und Grafikschnittstellen benötigt, wurde es im System als **optional** konzipiert:

* **In Docker (Standard aktiviert):** Im aktuellen Docker-Setup (`Dockerfile`) wird Docling mitsamt seiner Abhängigkeiten standardmäßig mit installiert. Löst automatisch aus, sobald Tabellen gefunden werden.  
  *Möchtest du ein leichtgewichtigeres Docker-Image bauen?* Öffne einfach die Datei `backend/Dockerfile` und kommentiere die Installation der `requirements-pdf.txt` aus. Das System fällt dann automatisch auf eine effiziente Standard-Textextraktion zurück.

* **Bei lokaler Installation (ohne Docker):**
  Wenn du das Python-Backend ohne Docker (z.B. in einer `venv`) entwickeln willst, kannst du selbst entscheiden, ob du Docling nutzt:
  ```bash
  # 1. Basis-Installation (Leichtgewichtig, Standard-PDF)
  pip install -r requirements.txt
  
  # 2. OPTIONAL: Installiere Docling für Tabellen-Support
  pip install -r requirements-pdf.txt
  ```
  Das Backend im Ordner `app/rag/decide_and_process.py` erkennt automatisch, ob du Docling installiert hast und passt die Verarbeitung entsprechend an!

## Server stoppen
Um die App und die Docker-Container wieder zu beenden, wechsle im Terminal in deinen Projektordner und führe aus:
```bash
docker-compose down
```
*(Deine hochgeladenen Dokumente und Vektor-Datenbanken im Ordner `/data` bleiben dabei sicher auf deiner Festplatte erhalten!)*
