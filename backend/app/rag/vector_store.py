import chromadb
from pathlib import Path
from chromadb.config import Settings

# Standardverzeichnis für die Vektordatenbank festlegen
DEFAULT_VECTOR_DB_DIR = (Path(__file__).parent.parent.parent / "data" / "vector_db").resolve()

def get_vector_db(persist_dir=None):
    # Persistenz-Pfad ermitteln (Standard oder benutzerdefiniert)
    if persist_dir is None:
        persist_path = DEFAULT_VECTOR_DB_DIR
    else:
        persist_path = Path(persist_dir).resolve()
    persist_path.mkdir(parents=True, exist_ok=True)

    # ChromaDB PersistentClient-Instanz initialisieren
    client = chromadb.PersistentClient(
        path=str(persist_path),
        settings=Settings(allow_reset=True, is_persistent=True)
    )
    
    # System-Cache leeren, um veraltete In-Memory-Indizes zu verhindern
    chromadb.api.client.SharedSystemClient.clear_system_cache() 

    # 'documents'-Collection abrufen oder neu anlegen
    collection = client.get_or_create_collection(
        name="documents" 
    )

    return collection