from __future__ import annotations
import fitz  # PyMuPDF
from dataclasses import dataclass
from typing import List


@dataclass
class PageText:
    page: int
    text: str


def extract_pdf_pages(pdf_path: str) -> List[PageText]:
    doc = fitz.open(pdf_path)
    pages: List[PageText] = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text("text") or ""
        # normalize whitespace a bit
        text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        pages.append(PageText(page=i + 1, text=text))
    doc.close()
    return pages