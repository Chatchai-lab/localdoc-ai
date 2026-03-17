import functools
from sentence_transformers import SentenceTransformer, CrossEncoder
import logging

# Unterdrücke Warnungen für sauberere API-Logs
logging.getLogger("rapidocr").setLevel(logging.ERROR)

@functools.lru_cache()
def get_bi_encoder():
    print(" Lade Bi-Encoder Modell...")
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@functools.lru_cache()
def get_cross_encoder():
    print("Lade Cross-Encoder Modell...")
    return CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')