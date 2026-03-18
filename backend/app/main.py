from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import time
from pathlib import Path
from typing import List, Dict, Any
from app.services.rag_service import RAGService
from app.rag.decide_and_process import IngestFactory
from fastapi.responses import StreamingResponse
from app.rag.generate import build_prompt, ollama_generate_stream
from fastapi.middleware.cors import CORSMiddleware
import json

# Definiere Datenverzeichnisse
# Im Docker läuft die App unter /app, lokal unter dem Projekt-Root
BASE_DIR = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"

# ============ Pydantic Models ============

class QueryRequest(BaseModel):
    """Request-Body für Suchanfragen."""
    question: str
    k: int = 3  # Top-k Ergebnisse
    rerank_k: int = 10  # Kandidaten vor Reranking
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Wie starte ich das Auto?",
                "k": 3,
                "rerank_k": 10
            }
        }


class SearchResult(BaseModel):
    """Ein einzelnes Suchergebnis."""
    score: float
    content: str
    source: str
    page: str
    method: str
    database: str


class QueryResponse(BaseModel):
    """Response für Suchanfragen."""
    results: List[SearchResult]
    latency_ms: int
    result_count: int


class DocumentUploadResponse(BaseModel):
    """Response für Datei-Upload."""
    message: str
    filename: str
    status: str


class HealthResponse(BaseModel):
    """Response für Health-Check."""
    status: str
    timestamp: float


# ============ FastAPI App ============

app = FastAPI(
    title="LocalDoc AI API",
    description="RAG API für lokale Dokumentensuche mit Docling + Chroma",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt alle Webseiten (wichtig für die Entwicklung)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt POST, GET, etc.
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health():
    """Health-Check Endpoint."""
    return HealthResponse(status="online", timestamp=time.time())


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Sucht in einer Frage basiert auf indexierten Dokumenten.
    
    Args:
        request: QueryRequest mit Frage und Parametern
        
    Returns:
        QueryResponse mit Suchergebnissen und Latenzen
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Frage darf nicht leer sein")
    
    start = time.time()
    
    try:
        results = RAGService.search_and_rerank(
            request.question, 
            k=request.k, 
            rerank_k=request.rerank_k
        )
        latency = int((time.time() - start) * 1000)
        
        # Konvertiere Dict-Ergebnisse zu Pydantic-Modellen
        search_results = [SearchResult(**result) for result in results]
        
        return QueryResponse(
            results=search_results,
            latency_ms=latency,
            result_count=len(search_results)
        )
    
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Nur PDF-Dateien erlaubt")
    
    # Pfad definieren: data/documents/dateiname.pdf
    upload_path = DOCUMENTS_DIR / file.filename
    
    try:
        # 1. Datei physisch auf die Festplatte schreiben
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Erst JETZT die Ingestion (Vektorisierung) starten
        IngestFactory.decide_and_process(str(upload_path))

        return DocumentUploadResponse(
            message=f"{file.filename} erfolgreich gespeichert und indexiert",
            filename=file.filename,
            status="success"
        )
    
    except Exception as e:
        # Falls was schief geht, Reste aufräumen
        if upload_path.exists():
            upload_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload-Fehler: {str(e)}")


@app.get("/documents")
def list_documents():
    """Listet alle Dokumente mit erweiterten Informationen auf."""
    if not DOCUMENTS_DIR.exists():
        return {"documents": [], "count": 0}
        
    docs = sorted(DOCUMENTS_DIR.glob("*.pdf"))
    document_list = []
    
    for d in docs:
        stats = d.stat()
        document_list.append({
            "name": d.name,
            "size_kb": round(stats.st_size / 1024, 2),
            "modified": stats.st_mtime  # Nützlich für "Sortieren nach Datum"
        })
        
    return {
        "documents": document_list,
        "count": len(document_list)
    }

@app.get("/stats")
def get_stats():
    """Gibt Statistiken über die Dokumentatur zurück."""
    return RAGService.get_document_stats()

@app.post("/ask/stream")
async def ask_stream(request: QueryRequest):
    query = request.question
    # 1. Nutze den funktionierenden RAG-Service
    search_results = RAGService.search_and_rerank(query, k=request.k)

    if not search_results:
        async def error_gen():
            yield "Dazu finde ich leider nichts in den Dokumenten."
        return StreamingResponse(error_gen(), media_type="text/plain")
    
    # 2. Formatiere die Ergebnisse & extrahiere Quellen
    formatted_context = []
    sources_for_frontend = []
    
    for res in search_results:
        formatted_context.append({
            "text": res["content"],
            "source": res["source"],
            "page": res["page"]
        })

        sources_for_frontend.append({
            "source": res["source"],
            "page": res["page"]
        })

    # 3. Erstelle prompt
    prompt = build_prompt(query, formatted_context)

    # 4. Generator-Funktion, die erst Text und dann Metadaten schickt
    async def combined_generator():
        # Erst den KI-Text streamen
        async for chunk in ollama_generate_stream(prompt):
            yield chunk
        
        yield f" [SOURCES] {json.dumps(sources_for_frontend)}"

    return StreamingResponse(
        combined_generator(), 
        media_type="text/event-stream"
    )


@app.delete("/documents/{filename}")
async def delete_document_endpoint(filename: str):
    """API-Endpunkt zum löschen eines Dokuments"""
    try: 
        result = RAGService.delete_document(filename)
        
        file_path = DOCUMENTS_DIR / filename
        if file_path.exists():
            file_path.unlink()

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")