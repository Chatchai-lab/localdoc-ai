from __future__ import annotations
from typing import List


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    verbesserte Version der Textchunking-Funktion, die versucht, Worte nicht zu zerschneiden.
    """
    if not text:
        return []

    text = " ".join(text.split())  # collapse whitespace
    chunks: List[str] = []

    n = len(text)
    start = 0
    step_size = max(1, chunk_size - overlap)  # Ensure we advance

    while start < n:
        end = min(start + chunk_size, n)

        if end < n:
            # Look for sentence endings first within the chunk
            last_sentence_end = -1
            for char in ".!?":
                pos = text.rfind(char, start, end)
                if pos > last_sentence_end:
                    last_sentence_end = pos
            
            if last_sentence_end != -1:
                end = last_sentence_end + 1
            else:
                # Look for word boundaries
                last_space = text.rfind(" ", start, end)
                if last_space != -1:
                    end = last_space

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        # Advance by step_size
        start += step_size
        
        # If we're close to the end, just finish
        if start >= n - 10:
            remaining = text[end:n].strip()
            if remaining:
                chunks.append(remaining)
            break

    return chunks 