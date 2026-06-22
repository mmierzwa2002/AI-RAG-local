"""

Konfiguracja aplikacji RAG.

"""
import os

# Adres lokalnego serwera Ollama (domyslnie po instalacji nasluchuje na 11434)
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Model jezykowy (LLM) uzywany do generowania odpowiedzi.
DEFAULT_LLM_MODEL = os.environ.get("DEFAULT_LLM_MODEL", "gemma3:4b")

# Model do embeddingow (zamiany tekstu na wektory).
# UWAGA: tego NIE zmieniamy w trakcie dzialania - wszystkie dokumenty w bazie
# musza byc zwektoryzowane tym samym modelem, inaczej wyszukiwanie nie ma sensu.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "nomic-embed-text")

# Fallback do rozpoznawania modeli embeddingowych po nazwie - uzywany TYLKO,
# gdy Ollama nie zwraca pola 'capabilities' (starsze wersje). Nowsze Ollamy
# raportuja 'embedding' vs 'completion' i wtedy ta lista jest nieuzywana.
EMBEDDING_HINTS = ("embed", "bge", "minilm", "arctic-embed", "mxbai")

# --- Parametry RAG ---
CHUNK_SIZE = 900      # maksymalny rozmiar fragmentu (w znakach)
CHUNK_OVERLAP = 150   # zachodzenie fragmentow na siebie (kontekst na stykach)
TOP_K = 4             # ile najlepiej pasujacych fragmentow trafia do promptu

# Temperatura generowania (0 = deterministycznie/konkretnie, 1 = kreatywnie).
# 0 trzyma model blisko kontekstu - mniej "dopowiadania" z wiedzy wlasnej.
LLM_TEMPERATURE = 0.0

# --- Pliki ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")   # oryginalne wgrane pliki
STORE_DIR = os.path.join(DATA_DIR, "store")      # baza wektorowa na dysku

ALLOWED_EXTENSIONS = {".txt", ".md", ".markdown", ".pdf"}
MAX_CONTENT_MB = 25  # limit rozmiaru pojedynczego pliku
