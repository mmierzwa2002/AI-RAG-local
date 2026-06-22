"""
Rdzen systemu RAG.

Sklada sie z czterech elementow:
  1. OllamaClient  - rozmowa z lokalnym serwerem Ollama (embeddingi, generowanie, lista modeli)
  2. parsowanie    - wyciaganie czystego tekstu z plikow (txt / md / pdf)
  3. chunkowanie   - dzielenie dlugiego tekstu na mniejsze fragmenty
  4. VectorStore   - prosta baza wektorowa na numpy (zapis na dysk + wyszukiwanie kosinusowe)
  5. RagEngine     - sklada to w calosc: dodawanie dokumentow i odpowiadanie na pytania
"""
import os
import re
import json
import unicodedata
import requests
import numpy as np

import config


# ----------------------------------------------------------------------------
# 1. Klient Ollama
# ----------------------------------------------------------------------------
class OllamaClient:
    """Cienka warstwa nad REST API Ollamy."""

    def __init__(self, base_url=config.OLLAMA_URL):
        self.base_url = base_url.rstrip("/")

    def is_available(self):
        """Czy serwer Ollama w ogole odpowiada?"""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self):
        """Zwraca liste nazw zainstalowanych modeli (np. ['gemma3:4b', 'nomic-embed-text'])."""
        r = requests.get(f"{self.base_url}/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json()
        return [m["name"] for m in data.get("models", [])]

    def can_generate(self, model):
        """Czy model nadaje sie do generowania tekstu (a nie tylko do embeddingow)?

        Pytamy Ollame przez /api/show o 'capabilities': modele embeddingowe
        (np. nomic-embed-text, bge-m3) maja tylko 'embedding', a czatowe maja
        'completion'. Gdy starsza Ollama nie zwraca tego pola, wracamy do
        heurystyki po nazwie (config.EMBEDDING_HINTS).
        """
        try:
            r = requests.post(f"{self.base_url}/api/show", json={"model": model}, timeout=10)
            r.raise_for_status()
            caps = r.json().get("capabilities") or []
        except requests.RequestException:
            caps = []
        if caps:
            return "completion" in caps
        name = model.lower()
        return not any(hint in name for hint in config.EMBEDDING_HINTS)

    def embed(self, text):
        """Zamienia tekst na wektor liczb (embedding)."""
        r = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": config.EMBEDDING_MODEL, "prompt": text},
            timeout=120,
        )
        r.raise_for_status()
        emb = r.json().get("embedding")
        if not emb:
            raise RuntimeError("Ollama nie zwrocila embeddingu - czy model embeddingowy jest pobrany?")
        return emb

    def generate(self, model, prompt):
        """Generuje odpowiedz modelu jezykowego na podstawie promptu."""
        r = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": config.LLM_TEMPERATURE},
            },
            timeout=300,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()


# ----------------------------------------------------------------------------
# 2. Parsowanie plikow -> czysty tekst
# ----------------------------------------------------------------------------
# Punktory z fontow Symbol/Wingdings PDF koduje w obszarze Private Use Area
# (np. 0xF0B4) - bez glifu w przegladarce widac "kwadraciki". Mapujemy je na "- ".
_BULLET_GLYPHS = {0xF0B4, 0xF0A7, 0xF0B7, 0xF0A8, 0xF0FC, 0xF0D8, 0x25AA, 0x2022}


def _clean_pdf_text(text):
    """Porzadkuje tekst wyciagniety z PDF, zeby byl czytelny i dobrze sie wektoryzowal:
    - NFKC: znaki zgodnosciowe na zwykle (matematyczne litery -> ASCII, ligatury),
    - punktory z fontow symbolicznych (Private Use Area) -> "- ",
    - usuwa pozostale niewyswietlalne znaki z obszaru PUA.
    """
    text = unicodedata.normalize("NFKC", text)
    out = []
    for ch in text:
        cp = ord(ch)
        if cp in _BULLET_GLYPHS:
            out.append("- ")
        elif 0xE000 <= cp <= 0xF8FF:   # Private Use Area - niewyswietlalne, pomijamy
            continue
        else:
            out.append(ch)
    return "".join(out)


def extract_text(filepath):
    """Wyciaga tekst z pliku w zaleznosci od rozszerzenia."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".txt", ".md", ".markdown"):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if ext == ".pdf":
        import fitz  # PyMuPDF - szybka i uniwersalna ekstrakcja tekstu z PDF
        with fitz.open(filepath) as doc:
            pages = [page.get_text("text") for page in doc]
        return _clean_pdf_text("\n\n".join(pages))

    raise ValueError(f"Nieobslugiwany typ pliku: {ext}")


# ----------------------------------------------------------------------------
# 3. Chunkowanie
# ----------------------------------------------------------------------------
def chunk_text(text, chunk_size=config.CHUNK_SIZE, overlap=config.CHUNK_OVERLAP):
    """
    Dzieli tekst na fragmenty o dlugosci ~chunk_size znakow.
    Stara sie ciac na granicy akapitu/zdania/spacji, zeby nie rwac slow w polowie.
    Sasiednie fragmenty zachodza na siebie o `overlap` znakow (kontekst na stykach).
    """
    # normalizacja bialych znakow
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)

        # jesli to nie koniec tekstu - znajdz sensowne miejsce ciecia
        if end < n:
            window = text[start:end]
            # preferuj koniec akapitu, potem koniec zdania, na koncu spacje
            candidates = [
                window.rfind("\n\n"),
                window.rfind(". "),
                window.rfind("? "),
                window.rfind("! "),
                window.rfind("\n"),
            ]
            break_at = max(candidates)
            if break_at < chunk_size * 0.5:  # za blisko poczatku -> tnij na spacji
                space = window.rfind(" ")
                if space > chunk_size * 0.5:
                    break_at = space
            if break_at > chunk_size * 0.5:
                end = start + break_at + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # doszlismy do konca tekstu -> ostatni fragment dodany, konczymy
        if end >= n:
            break

        # przesun okno do przodu (z zachowaniem zachodzenia), zawsze co najmniej o 1 znak
        start = max(end - overlap, start + 1)

    return chunks


# ----------------------------------------------------------------------------
# 4. Baza wektorowa (numpy + zapis na dysk)
# ----------------------------------------------------------------------------
class VectorStore:
    """
    Minimalna baza wektorowa.
    Trzyma macierz embeddingow (numpy) i liste metadanych (z czego pochodzi fragment).
    Wyszukiwanie = podobienstwo kosinusowe miedzy pytaniem a fragmentami.
    """

    def __init__(self, store_dir=config.STORE_DIR):
        self.store_dir = store_dir
        self.emb_path = os.path.join(store_dir, "embeddings.npy")
        self.meta_path = os.path.join(store_dir, "meta.json")

        os.makedirs(store_dir, exist_ok=True)

        self.embeddings = np.zeros((0, 0), dtype=np.float32)
        self.meta = []  # lista slownikow: {doc_name, chunk_index, text}
        self._load()

    # --- trwalosc ---
    def _load(self):
        if os.path.exists(self.emb_path) and os.path.exists(self.meta_path):
            self.embeddings = np.load(self.emb_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)

    def _save(self):
        np.save(self.emb_path, self.embeddings)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False)

    # --- operacje ---
    def add_document(self, doc_name, chunks, embeddings):
        """Dodaje fragmenty jednego dokumentu wraz z ich embeddingami."""
        new = np.asarray(embeddings, dtype=np.float32)
        if self.embeddings.shape[0] == 0:
            self.embeddings = new
        else:
            self.embeddings = np.vstack([self.embeddings, new])

        for i, text in enumerate(chunks):
            self.meta.append({"doc_name": doc_name, "chunk_index": i, "text": text})

        self._save()

    def search(self, query_embedding, top_k=config.TOP_K):
        """Zwraca top_k najbardziej podobnych fragmentow z wynikiem podobienstwa."""
        if self.embeddings.shape[0] == 0:
            return []

        q = np.asarray(query_embedding, dtype=np.float32)
        E = self.embeddings

        # podobienstwo kosinusowe: (E . q) / (|E| * |q|)
        denom = (np.linalg.norm(E, axis=1) * np.linalg.norm(q)) + 1e-8
        sims = (E @ q) / denom

        k = min(top_k, len(sims))
        # indeksy k najwyzszych wynikow, posortowane malejaco
        top_idx = np.argpartition(-sims, k - 1)[:k]
        top_idx = top_idx[np.argsort(-sims[top_idx])]

        results = []
        for idx in top_idx:
            item = dict(self.meta[idx])
            item["score"] = float(sims[idx])
            results.append(item)
        return results

    def list_documents(self):
        """Lista dokumentow w bazie wraz z liczba fragmentow."""
        counts = {}
        for m in self.meta:
            counts[m["doc_name"]] = counts.get(m["doc_name"], 0) + 1
        return [{"name": name, "chunks": c} for name, c in sorted(counts.items())]

    def delete_document(self, doc_name):
        """Usuwa wszystkie fragmenty danego dokumentu."""
        keep = [i for i, m in enumerate(self.meta) if m["doc_name"] != doc_name]
        if len(keep) == len(self.meta):
            return False  # nic nie usunieto

        self.meta = [self.meta[i] for i in keep]
        self.embeddings = self.embeddings[keep] if keep else np.zeros((0, 0), dtype=np.float32)
        self._save()
        return True

    def total_chunks(self):
        return len(self.meta)


# ----------------------------------------------------------------------------
# 5. Silnik RAG (spina wszystko razem)
# ----------------------------------------------------------------------------
PROMPT_TEMPLATE = """Jestes asystentem, ktory odpowiada na pytania TYLKO i WYLACZNIE na podstawie
fragmentow z sekcji KONTEKST. Te fragmenty sa jedynym dozwolonym zrodlem prawdy.

ZASADY (przestrzegaj ich bezwzglednie):
1. Nie korzystaj z wiedzy spoza KONTEKSTU. Nie dopowiadaj i nie zgaduj.
2. Po kazdym stwierdzeniu podaj zrodlo w nawiasie kwadratowym, np. [Fragment 2].
   Jesli opiera sie na kilku fragmentach, wymien je wszystkie: [Fragment 1][Fragment 3].
3. Jesli w KONTEKSCIE nie ma odpowiedzi, napisz dokladnie:
   "Nie znajduje tej informacji w dokumentach." i nie dodawaj nic wiecej.
4. Jesli kontekst odpowiada tylko czesciowo, napisz co wynika z dokumentow (z cytatami)
   i wyraznie zaznacz, czego w nich brakuje.
5. Odpowiadaj po polsku, rzeczowo i zwiezle.

=== KONTEKST ===
{context}

=== PYTANIE ===
{question}

=== ODPOWIEDZ (z cytatami [Fragment N]) ==="""


class RagEngine:
    def __init__(self):
        self.client = OllamaClient()
        self.store = VectorStore()

    # --- dodawanie dokumentu ---
    def add_document(self, filepath, doc_name):
        """Pelny pipeline: plik -> tekst -> fragmenty -> embeddingi -> baza."""
        text = extract_text(filepath)
        if not text.strip():
            raise ValueError("Nie udalo sie wyciagnac tekstu z pliku (moze to skan/obraz?).")

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("Dokument jest pusty po przetworzeniu.")

        embeddings = [self.client.embed(c) for c in chunks]
        self.store.add_document(doc_name, chunks, embeddings)
        return {"chunks": len(chunks), "chars": len(text)}

    # --- odpowiadanie na pytanie ---
    def query(self, question, model=None, top_k=config.TOP_K):
        """Retrieval + generation. Zwraca odpowiedz i wykorzystane zrodla."""
        model = model or config.DEFAULT_LLM_MODEL

        if self.store.total_chunks() == 0:
            return {
                "answer": "Baza wiedzy jest pusta. Dodaj najpierw jakis dokument po lewej stronie.",
                "sources": [],
                "model": model,
            }

        # 1. zamien pytanie na wektor i znajdz pasujace fragmenty
        q_emb = self.client.embed(question)
        sources = self.store.search(q_emb, top_k=top_k)

        # 2. zbuduj kontekst z najlepszych fragmentow
        context_parts = []
        for i, s in enumerate(sources, 1):
            context_parts.append(f"[Fragment {i} | {s['doc_name']}]\n{s['text']}")
        context = "\n\n".join(context_parts)

        # 3. zapytaj model jezykowy
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        answer = self.client.generate(model, prompt)

        return {"answer": answer, "sources": sources, "model": model}
