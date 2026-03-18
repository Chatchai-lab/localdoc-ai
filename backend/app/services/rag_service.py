"""
RAG Service - Enthält die Geschäftslogik für Dokumentensuche und Reranking.
"""
from typing import List, Dict, Any
from pathlib import Path
from app.services.models import get_bi_encoder, get_cross_encoder
from app.rag.vector_store import get_vector_db
import time

CURRENT_FILE = Path(__file__).resolve()
# Docker: /app
# Local: localdoc-ai/
BASE_DIR = Path("/app") if Path("/app").exists() else CURRENT_FILE.parent.parent.parent.parent

DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
VECTOR_DB_DOCLING_DIR = DATA_DIR / "vector_db_docling"


class RAGService:
    """Service für semantische Dokumentensuche mit Reranking."""
    
    @staticmethod
    def search_and_rerank(query: str, k: int = 3, rerank_k: int = 10) -> List[Dict[str, Any]]:
    
        try:
            bi_encoder = get_bi_encoder()
            reranker = get_cross_encoder()

            query_embedding = bi_encoder.encode(f"query: {query}").tolist()
            all_results = []

            #Phase 1: Sicherer Retrieval aus beiden Datenbanken
            for db_path, source_db in [(VECTOR_DB_DIR, "standard"), (VECTOR_DB_DOCLING_DIR, "docling")]:
                if db_path.exists() and any(db_path.iterdir()):
                    try:
                        db = get_vector_db(persist_dir=str(db_path))
                        res = db.query(query_embeddings=[query_embedding], n_results=rerank_k)
                        
                        print(f"--- DEBUG SUCHE ---")
                        print(f"DB: {source_db} | Einträge in DB: {db.count()}")
                        found_count = len(res['documents'][0]) if res['documents'] else 0
                        print(f"Ergebnisse für '{query}': {found_count}")
                        
                        all_results.append((res, source_db))
                    except Exception as e:
                        print(f"Überspringe Db {source_db}: {e}")
            
            
            # Phase 2: Sammeln & Deduplizieren
            seen = set()
            candidates = []
            for res, source_db in all_results:
                if res["documents"] and res["documents"][0]:
                    for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
                        doc_hash = hash(doc)
                        if doc_hash not in seen:
                            seen.add(doc_hash)
                            meta["source_db"] = source_db
                            candidates.append((doc, meta))
            
            if not candidates:
                return []

            # Phase 3: Reranking mit Cross-Encoder
            scores = reranker.predict([[query, c[0]] for c in candidates])
            scored = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
            
            # Phase 4: Formatierung für API
            results = []
            for score, (doc, meta) in scored[:k]:
                results.append({
                    "score": float(score),
                    "content": doc,
                    "source": Path(meta.get("source", "unknown")).name,
                    "page": str(meta.get("page_label") or meta.get("page") or "N/A"),
                    "method": meta.get("method", "standard"),
                    "database": meta.get("source_db", "unknown")
                })
            return results
        
        except Exception as e:
            raise RuntimeError(f"Fehler bei der Dokumentensuche: {str(e)}")
    
    @staticmethod
    def get_document_stats() -> Dict[str, Any]:
        """Gibt Statistiken über indexierte Dokumente zurück."""
        counts = {"standard": 0, "docling": 0}

        for db_path, key in [(VECTOR_DB_DIR, "standard"), (VECTOR_DB_DOCLING_DIR, "docling")]:
            if db_path.exists() and any(db_path.iterdir()):
                try:
                    db = get_vector_db(persist_dir=str(db_path))
                    counts[key] = db.count()
                except Exception as e:
                    counts[key] = 0 

        return {
         "status": "online",
         "documents_counts": counts,
         "paths": {
             "standard": str(VECTOR_DB_DIR),
             "docling": str(VECTOR_DB_DOCLING_DIR)
         }
        }
        
        
    @classmethod
    def delete_document(cls, filename: str):
        """Löscht ein Dokument und erzwingt die Bereinigung der Datenbank."""
        
        # 1. Datenbank-Bereinigung
        for db_path in [VECTOR_DB_DIR, VECTOR_DB_DOCLING_DIR]:
            if db_path.exists() and any(db_path.iterdir()):
                try:
                    db = get_vector_db(persist_dir=str(db_path))
                    
                    #1. SChritt: Alle IDs finden, die zum Namen passen
                    all_data = db.get() 
                    ids_to_delete = []
                    if all_data and "ids" in all_data:
                        for i in range(len(all_data["ids"])):
                            meta = all_data["metadatas"][i] if all_data["metadatas"] else {}
                            source = meta.get("source", "")
                            # Wenn der Dateiname im Quellpfad vorkommt -> Weg damit!
                            if filename in source or filename.replace(".pdf", "") in source:
                                ids_to_delete.append(all_data["ids"][i])
                    
                    if ids_to_delete:
                        db.delete(ids=ids_to_delete)
                        db = get_vector_db(persist_dir=str(db_path))
                        print(f"DEBUG: {len(ids_to_delete)}IDs aus {db_path.name} gelöscht")

                        _=db.count()
                        
                except Exception as e:
                    print(f"DB Error in {db_path.name}: {e}")

        # 2. PDF-Datei löschen
        clean_name = filename.replace(".pdf", "")
        DOCUMENTS_PATH = DATA_DIR / "documents"
        pdf_file = DOCUMENTS_PATH / f"{clean_name}.pdf"
        if pdf_file.exists():
            pdf_file.unlink()

        # 3. Processed-Ordner bereinigen
        PROCESSED_PATH = DATA_DIR/ "processed"
        if PROCESSED_PATH.exists():
            for p_file in PROCESSED_PATH.glob(f"*{clean_name}*"):
                try:
                    p_file.unlink()
                except:
                    pass

        time.sleep(0.3)
        
        return {"status": "success", "message": f"Bereinigung für {filename} abgeschlossen."}