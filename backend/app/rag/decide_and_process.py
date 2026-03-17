import os
import subprocess
import sys
import logging
from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption


# Wir importieren den neuen Spezial-Weg
from app.rag.ingest_docling import run_docling_ingest

# Definiere Datenverzeichnisse relativ zu diesem Skript
# decide_and_process.py liegt in backend/app/rag/, also ist ../../../data/ = localdoc-ai/data/
BASE_DIR = Path(__file__).parent.parent.parent.parent  # localdoc-ai/
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

#Debug Prints
print(f"DEBUG: BASE_DIR ist {BASE_DIR.resolve()}")
print(f"DEBUG: PROCESSED_DIR ist {PROCESSED_DIR.resolve()}")

class IngestFactory:
    _converter_cache = None

    @classmethod
    def get_converter(cls):
        """Lädt den Konverter nur einmalig in den RAM (Singleton Pattern)
        OCR ist deaktiviert für digitale PDFs (massive Speedup!)
        """
        if cls._converter_cache is None:
            print(" Initialisiere Docling DocumentConverter (OCR deaktiviert)...")
            # Unterdrücke RapidOCR Warnungen
            logging.getLogger("rapidocr").setLevel(logging.ERROR)
            
            # Konfiguriere PDF-Optionen: OCR aus, Tabellenstruktur an
            pdf_options = PdfPipelineOptions(
                do_ocr=False,  # Deaktiviere OCR für digitale PDFs
                do_table_structure=True  # Erkenne Tabellen weiterhin
            )
            
            # Erstelle Format-Optionen für PDF
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options)
            }
            
            # Initialisiiere DocumentConverter mit optimierten Optionen
            cls._converter_cache = DocumentConverter(
                format_options=format_options
            )
        return cls._converter_cache

    @classmethod
    def decide_and_process(cls, pdf_path_str: str):
        pdf_path = Path(pdf_path_str)
        if not pdf_path.exists():
            print(f" Datei nicht gefunden: {pdf_path_str}")
            return

        print(f" Analyse des Layouts von '{pdf_path.name}'...")
        
        # 1. Schneller Check mit Docling auf Tabellen (verwendet gecachten Konverter)
        converter = cls.get_converter()
        
        try:
            render_result = converter.convert(str(pdf_path))
            # Wir zählen die erkannten Tabellen-Elemente
            table_count = sum(1 for item, _ in render_result.document.iterate_items() if hasattr(item, 'label') and item.label == "table")
            
            if table_count > 0:
                print(f"💡 {table_count} Tabelle(n) gefunden. Nutze Docling-Spezialpfad.")
                # Pfad B: Direktes Ingest + Embedding in vector_db_docling
                run_docling_ingest(pdf_path)
            else:
                print(" Reiner Text erkannt. Triggere deine Standard-Kette...")
                
                # --- SCHRITT 1: DEIN INGEST.PY ---
                # Wir rufen dein Skript exakt so auf, wie du es manuell tun würdest
                print(" Schritt 1/2: Erzeuge JSONL (ingest.py)...")
                subprocess.run([
                    sys.executable, "-m", "app.rag.ingest", 
                    "--in", str(pdf_path.parent), 
                    "--out", str(PROCESSED_DIR)
                ], check=True, cwd=str(BASE_DIR/"backend")) 

                # --- SCHRITT 2: DEIN EMBED.PY ---
                # Sobald die JSONL da ist, triggern wir das Embedding
                print(" Schritt 2/2: Erzeuge Vektoren (embed.py)...")
                subprocess.run([
                    sys.executable, "-m", "app.rag.embed"
                ], check=True, cwd=str(BASE_DIR/ "backend"))
                
                print(f" Standard-Kette für '{pdf_path.name}' erfolgreich abgeschlossen.")

        except Exception as e:
            print(f" Fehler bei der Analyse: {e}. Nutze Sicherheits-Pfad (Docling).")
            run_docling_ingest(pdf_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Verarbeite alle übergebenen PDF-Pfade
        for pdf_path in sys.argv[1:]:
            print(f"\n{'='*60}")
            IngestFactory.decide_and_process(pdf_path)
        print(f"\n{'='*60}")
        print(" Alle PDFs wurden verarbeitet!")
    else:
        print("Gebrauch: python -m app.rag.decide_and_process <PFAD_ZUM_PDF> [PFAD_ZUM_PDF2 ...]")