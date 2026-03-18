import os
from pathlib import Path
from docling.document_converter import DocumentConverter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Abhängigkeiten für Vektordatenbank und Embedding-Modelle
from app.rag.vector_store import get_vector_db
from app.services.models import get_bi_encoder

# Basis-Verzeichnis dynamisch ermitteln (Docker vs. Lokal)
BASE_DIR = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DOCLING_DIR = DATA_DIR / "vector_db_docling"

def run_docling_ingest(pdf_path: Path):
    print(f"Starte Docling-Verarbeitung für: {pdf_path.name}")

    # 1. Dokument mit Layout-Erhaltung in strukturiertes Markdown konvertieren
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    markdown_content = result.document.export_to_markdown()

    # 2. Textsegmentierung basierend auf Textlänge und Markdown-Formatierung (z.B. Tabellen)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "|", " ", ""]
    )
    chunks = text_splitter.split_text(markdown_content)
    
    # 3. Vektordatenbank und Embedding-Modell für Docling-Inhalte initialisieren
    collection = get_vector_db(persist_dir=str(VECTOR_DB_DOCLING_DIR))
    bi_encoder = get_bi_encoder()

    print(f"Erstelle Vektoren für {len(chunks)} Text-Abschnitte...")

    # 4. Text-Chunks in Vektor-Embeddings umwandeln und in die Datenbank schreiben
    for i, chunk_text in enumerate(chunks):
        embedding = bi_encoder.encode(chunk_text).tolist()
        
        collection.add(
            ids=[f"dl_{pdf_path.stem}_{i}"],
            embeddings=[embedding],
            documents=[chunk_text],
            metadatas=[{
                "source": pdf_path.name, 
                "page": "N/A (Docling-Fullscan)",
                "method": "docling_markdown"
            }]
        )
    print(f" Docling-Daten erfolgreich in '{VECTOR_DB_DOCLING_DIR}' gespeichert.")