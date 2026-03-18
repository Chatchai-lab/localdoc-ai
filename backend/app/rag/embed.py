import json
import glob
from pathlib import Path
from sentence_transformers import SentenceTransformer
from app.rag.vector_store import get_vector_db

# Basis-Verzeichnis dynamisch ermitteln (Docker vs. Lokal)
BASE_DIR = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
PROCESSED_DIR = DATA_DIR / "processed"

# Embedding-Modell laden
model = SentenceTransformer("intfloat/multilingual-e5-small")

# Verbindung zur Vektordatenbank herstellen
collection = get_vector_db(persist_dir=str(VECTOR_DB_DIR))

def load_chunks():
    """Lädt alle verarbeiteten Text-Chunks aus den JSONL-Dateien."""
    files = glob.glob(str(PROCESSED_DIR / "*.jsonl"))

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)

def main():

    documents = []
    ids = []
    metadatas = []

    for chunk in load_chunks():

        text = chunk["text"]

        documents.append(text)
        ids.append(chunk["chunk_id"])
        metadatas.append({
            "source": chunk["source"],
            "page": chunk["page"]
        })

    if not documents:
        print("Keine Dokumente zum Einbetten gefunden.")
        return

    # Embeddings (Vektorrepräsentationen) generieren
    embeddings = model.encode(documents)

    # In Vektordatenbank speichern
    collection.add(
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print("Embeddings erfolgreich gespeichert.")

if __name__ == "__main__":
    main()