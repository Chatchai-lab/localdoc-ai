from __future__ import annotations
from typing import List


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Führt Text-Chunking durch und berücksichtigt dabei Wortgrenzen und Satzenden, 
    um den inhaltlichen Kontext beim Schneiden bestmöglich zu erhalten.
    """
    if not text:
        return []

    text = " ".join(text.split())  # Mehrfache Leerzeichen normieren
    chunks: List[str] = []

    n = len(text)
    start = 0
    step_size = max(1, chunk_size - overlap)  # Fortschritt sicherstellen, um Endlosschleifen zu vermeiden

    while start < n:
        end = min(start + chunk_size, n)

        if end < n:
            # Bevorzugt an Satzenden trennen, um Kontextverlust zu minimieren
            last_sentence_end = -1
            for char in ".!?":
                pos = text.rfind(char, start, end)
                if pos > last_sentence_end:
                    last_sentence_end = pos
            
            if last_sentence_end != -1:
                end = last_sentence_end + 1
            else:
                # Alternativ an der letzten bekannten Wortgrenze (Leerzeichen) trennen
                last_space = text.rfind(" ", start, end)
                if last_space != -1:
                    end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        # Startposition um die berechnete Schrittgröße (unter Berücksichtigung des Overlaps) verschieben
        start += step_size
        
        # Wenn nur noch ein minimaler Rest bleibt, diesen als letzten Chunk anfügen und abschließen
        if start >= n - 10:
            remaining = text[end:n].strip()
            if remaining:
                chunks.append(remaining)
            break

    return chunks 