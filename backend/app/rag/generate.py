from __future__ import annotations
import httpx
import json
from typing import List, Dict, Any, Generator, AsyncGenerator

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.1"

def build_prompt(question: str, contexts: List[Dict[str, Any]]) -> str:
    ctx_blocks = [f"[{i+1}] Quelle: {c['source']} (S.{c['page']})\n{c['text']}" for i, c in enumerate(contexts)]
    ctx_text = "\n\n".join(ctx_blocks)
    return f"""Beantworte die Frage NUR mit dem Kontext. Falls unbekannt, sag: "Dazu finde ich nichts."
Frage: {question}
Kontext:
{ctx_text}
Antworte auf Deutsch. Max 10 Sätze. Quellen am Ende: "- Datei S.Seite" """

async def ollama_generate_stream(prompt: str) -> AsyncGenerator[str, None]:
    """Gibt die Antwort asynchron Wort für Wort zurück."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0.2}
    }
    
    try:
        # Wir nutzen den AsyncClient für FastAPI
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/generate", json=payload) as r:
                if r.status_code != 200:
                    yield f"Fehler: Ollama liefert Status {r.status_code}."
                    return

                async for line in r.aiter_lines(): # aiter_lines statt iter_lines
                    if line:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break
                            
    except httpx.ConnectError:
        yield "Fehler: Verbindung zu Ollama fehlgeschlagen. Läuft die Ollama App?"
    except Exception as e:
        yield f"\n[Fehler]: {str(e)}"