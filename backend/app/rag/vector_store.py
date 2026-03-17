import chromadb
from pathlib import Path

# Definiere Standard-Verzeichnis relativ zu diesem Skript
# vector_store.py liegt in backend/app/rag/, also ist ../../../data/vector_db = localdoc-ai/data/vector_db
DEFAULT_VECTOR_DB_DIR = (Path(__file__).parent.parent.parent / "data" / "vector_db").resolve()

def get_vector_db(persist_dir=None):
    # Verwende default persist_dir, wenn nicht angegeben
    if persist_dir is None:
        persist_path = DEFAULT_VECTOR_DB_DIR
    else:
        persist_path = Path(persist_dir).resolve()
    persist_path.mkdir(parents=True, exist_ok=True)

    # 2. Den Client am spezifischen Pfad starten
    client = chromadb.PersistentClient(
        path=str(persist_path)
    )

    # 3. Die Collection holen oder erstellen
    collection = client.get_or_create_collection(
        name="documents" 
    )

    return collection