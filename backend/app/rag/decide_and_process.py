import os
import subprocess
import sys
import logging
from pathlib import Path

# Optionales Docling-Modul importieren
try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import PdfFormatOption
    from app.rag.ingest_docling import run_docling_ingest
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    logging.warning("Docling-Modul fehlt - Nutzung der Standard-Verarbeitungspipeline")

# Dynamische Ermittlung des Basis-Pfades anhand der Umgebung (Docker vs. Lokal)
BASE_DIR = Path("/app") if Path("/app").exists() else Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

class IngestFactory:
    _converter_cache = None

    @classmethod
    def get_converter(cls):
        """
        Singleton-Initialisierung des Docling-Konverters für Performance und RAM-Optimierung.
        Deaktiviert die optische Zeichenerkennung (OCR) zur Steigerung der Durchlaufstärke bei nativen PDFs.
        """
        if not DOCLING_AVAILABLE:
            return None
            
        if cls._converter_cache is None:
            logging.info("Initialisiere Docling DocumentConverter (OCR optimiert)")
            
            # Fehlerprotokollierung für die RapidOCR Komponente drosseln
            logging.getLogger("rapidocr").setLevel(logging.ERROR)
            
            # Deaktiviere OCR für Speedup
            pdf_options = PdfPipelineOptions()
            pdf_options.do_ocr = False
            pdf_options.do_table_structure = True
            
            # Format-Spezifikationen für das PDF-Dateiformat
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options)
            }
            
            # Persistenter Converter in der Applikationslebensdauer
            cls._converter_cache = DocumentConverter(
                format_options=format_options
            )
        return cls._converter_cache

    @classmethod
    def decide_and_process(cls, pdf_path_str: str):
        """Analysiert das Dokument und wählt je nach Inhalt (z.B. Tabellen) die passende Verarbeitungs-Pipeline aus."""
        pdf_path = Path(pdf_path_str)
        if not pdf_path.exists():
            logging.error(f"Quelldokument inexistent unter Pfad: {pdf_path_str}")
            return

        logging.info(f"Beginne Vorverarbeitung für Dokument: '{pdf_path.name}'")
        
        # Fallback, falls Docling nicht verfügbar ist
        if not DOCLING_AVAILABLE:
            logging.info("Docling ist nicht installiert - Fallback auf Standard-Pipeline")
            cls._run_standard_pipeline(pdf_path)
            return
        
        # Dokument analysieren und nach Tabellen-Elementen suchen
        converter = cls.get_converter()
        
        try:
            render_result = converter.convert(str(pdf_path))
            # Anzahl der identifizierten Tabellen zählen
            table_count = sum(1 for item, _ in render_result.document.iterate_items() if hasattr(item, 'label') and item.label == "table")
            
            if table_count > 0:
                logging.info(f"{table_count} Tabelle(n) im Dokument gefunden -> Verarbeite Dokument mit Docling-Pipeline")
                run_docling_ingest(pdf_path)
            else:
                logging.info("Keine komplexen Strukturen (Tabellen) gefunden -> Verarbeite Dokument mit Standard-Pipeline")
                cls._run_standard_pipeline(pdf_path)

        except Exception as e:
            logging.error(f"Fehler bei der Dokumentenanalyse: {e} -> Führe Fallback auf Standard-Pipeline aus")
            cls._run_standard_pipeline(pdf_path)

    @classmethod
    def _run_standard_pipeline(cls, pdf_path: Path):
        """Führt die reguläre PDF-Verarbeitung über ingest.py und embed.py aus (ohne Docling)."""
        # Korrektes Arbeitsverzeichnis ermitteln (Docker: /app, Lokal: ./backend)
        cwd_path = BASE_DIR / "backend"
        if not cwd_path.exists():
            cwd_path = BASE_DIR

        print(f" Schritt 1/2: Erzeuge JSONL mit ingest.py...")
        subprocess.run([
            sys.executable, "-m", "app.rag.ingest", 
            "--in", str(pdf_path.parent), 
            "--out", str(PROCESSED_DIR)
        ], check=True, cwd=str(cwd_path))

        print(f" Schritt 2/2: Erzeuge Vektoren mit embed.py...")
        subprocess.run([
            sys.executable, "-m", "app.rag.embed"
        ], check=True, cwd=str(cwd_path))
        
        print(f" ✓ Standard-Pipeline für '{pdf_path.name}' erfolgreich abgeschlossen.")

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