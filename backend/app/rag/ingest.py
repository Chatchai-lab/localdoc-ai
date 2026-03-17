from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Any, List

from app.utils.pdf import extract_pdf_pages
from app.utils.text import chunk_text


def stable_doc_id(file_path: Path) -> str:
    # stable id based on filename + file size (simple and good enough for now)
    st = file_path.stat()
    raw = f"{file_path.name}:{st.st_size}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def write_jsonl(out_path: Path, records: List[Dict[str, Any]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def ingest_pdf(pdf_path: Path, out_dir: Path, chunk_size: int, overlap: int) -> Path:
    doc_id = stable_doc_id(pdf_path)
    pages = extract_pdf_pages(str(pdf_path))

    records: List[Dict[str, Any]] = []
    chunk_counter = 0

    for p in pages:
        chunks = chunk_text(p.text, chunk_size=chunk_size, overlap=overlap)
        for c in chunks:
            chunk_counter += 1
            records.append(
                {
                    "doc_id": doc_id,
                    "source": pdf_path.name,
                    "page": p.page,
                    "method": "standard",
                    "chunk_id": f"{doc_id}-{chunk_counter:05d}",
                    "text": c,
                }
            )

    out_path = out_dir / f"{doc_id}_{pdf_path.stem}.jsonl"
    write_jsonl(out_path, records)
    return out_path


def main() -> None:
    # Definiere Standard-Ausgabeverzeichnis relativ zu diesem Skript
    # ingest.py liegt in backend/app/rag/, also ist ../../../data/processed = localdoc-ai/data/processed
    DEFAULT_OUT_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
    
    parser = argparse.ArgumentParser(description="Ingest PDFs into chunked JSONL.")
    parser.add_argument("--in", dest="in_dir", required=True, help="Input folder with PDFs")
    parser.add_argument("--out", dest="out_dir", default=str(DEFAULT_OUT_DIR), help="Output folder for JSONL (default: localdoc-ai/data/processed)")
    parser.add_argument("--chunk-size", type=int, default=1200)
    parser.add_argument("--overlap", type=int, default=200)

    args = parser.parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir).resolve()  # Absoluten Pfad verwenden

    pdfs = sorted(in_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {in_dir}")

    for pdf in pdfs:
        out_path = ingest_pdf(pdf, out_dir, args.chunk_size, args.overlap)
        print(f"Ingested {pdf.name} -> {out_path}")


if __name__ == "__main__":
    main()