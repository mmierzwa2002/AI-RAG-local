# RAG lokalny

Prosty, w pełni lokalny system **RAG** (Retrieval-Augmented Generation):
wgrywasz własne dokumenty, a model językowy odpowiada na pytania **wyłącznie na ich
podstawie**. Wszystko działa na Twoim komputerze — żadne dane nie wychodzą na zewnątrz.

```
        ┌─────────────┐   pytanie    ┌──────────────┐
        │  Frontend   │ ───────────► │    Flask     │
        │ (HTML/CSS)  │ ◄─────────── │   (app.py)   │
        └─────────────┘  odpowiedź   └──────┬───────┘
                                            │
                         ┌──────────────────┴──────────────────┐
              zapytanie ▼│▲ fragmenty             tekst ▼│▲ wynik
                ┌──────────────────┐        ┌──────────────────┐
                │  Baza wektorowa  │        │      Ollama      │
                │  numpy / rag.py  │        │ embeddingi + LLM │
                └──────────────────┘        └──────────────────┘
```

## Jak to działa (w skrócie)

1. **Dodanie dokumentu** → tekst jest dzielony na fragmenty (_chunki_), każdy fragment
   zamieniany jest na wektor (_embedding_) przez Ollamę i zapisywany w bazie wektorowej.
2. **Pytanie** → pytanie też staje się wektorem; baza znajduje najbardziej podobne
   fragmenty (podobieństwo kosinusowe); te fragmenty trafiają do promptu jako kontekst.
3. **Odpowiedź** → model językowy (domyślnie **Gemma 3**) generuje odpowiedź na podstawie
   kontekstu. Pod odpowiedzią widać źródła, z których skorzystał, wraz z trafnością.

---

## Wymagania

- **Python 3.10+**
- **[Ollama](https://ollama.com/download)** — lokalny serwer modeli AI

---

## Uruchomienie krok po kroku

### 1. Zainstaluj Ollamę i pobierz modele

Pobierz i zainstaluj Ollamę ze strony <https://ollama.com/download>.
Następnie w terminalu pobierz dwa modele — językowy i do embeddingów:

```bash
ollama pull gemma3:4b          # model językowy (domyślny)
ollama pull nomic-embed-text   # model do embeddingów (wektoryzacja tekstu)
```

> Ollama po instalacji sama uruchamia serwer w tle (`http://localhost:11434`).
> Możesz to sprawdzić komendą `ollama list` — powinna pokazać pobrane modele.

### 2. Przygotuj projekt

W folderze z projektem utwórz wirtualne środowisko i zainstaluj zależności:

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Uruchom aplikację

```bash
python app.py
```

Zobaczysz w terminalu adres aplikacji. Otwórz w przeglądarce:

```
http://localhost:5000
```

### 4. Korzystanie

1. W prawym górnym rogu sprawdź, czy świeci się **„ollama online”** (zielona kropka).
2. Po lewej stronie przeciągnij lub wybierz plik (`.txt`, `.md`, `.pdf`) — zostanie
   zaindeksowany.
3. U góry wybierz **model językowy** z listy (pobiera ją automatycznie z Ollamy)
   i ewentualnie liczbę fragmentów **k**.
4. Wpisz pytanie i kliknij **Zapytaj**. Pod odpowiedzią pojawią się źródła.

---

## Zmiana modelu

Model językowy zmienisz **bezpośrednio w interfejsie** — rozwijana lista pokazuje
wszystkie modele zainstalowane w Ollamie. Jeśli pobierzesz nowy model
(`ollama pull nazwa`), kliknij ikonę **↻** obok listy, żeby ją odświeżyć.

Aby zmienić **domyślny** model, edytuj `DEFAULT_LLM_MODEL` w pliku `config.py`.

> **Uwaga o modelu embeddingów:** model `nomic-embed-text` (ustawiany w `config.py`)
> odpowiada za wektoryzację. Nie zmieniaj go po dodaniu dokumentów — cała baza musi
> być zwektoryzowana jednym modelem, inaczej wyszukiwanie przestanie działać. Po zmianie
> trzeba usunąć folder `data/store/` i dodać dokumenty od nowa.

---

## Struktura projektu

```
rag-lokalny/
├── app.py              # serwer Flask (endpointy HTTP)
├── rag.py              # rdzeń RAG: chunking, embeddingi, baza wektorowa, generacja
├── config.py           # ustawienia (adres Ollamy, modele, parametry)
├── requirements.txt    # zależności Pythona
├── templates/
│   └── index.html      # interfejs
├── static/
│   ├── style.css       # style
│   └── app.js          # logika frontendu
└── data/               # tworzone automatycznie
    ├── uploads/        # oryginalne wgrane pliki
    └── store/          # baza wektorowa (embeddings.npy + meta.json)
```

## Najczęstsze problemy

| Objaw                     | Rozwiązanie                                                          |
| ------------------------- | -------------------------------------------------------------------- |
| „ollama offline”          | Uruchom Ollamę. Sprawdź `ollama list`. Domyślny port to 11434.       |
| Błąd przy dodawaniu pliku | Upewnij się, że pobrałeś `nomic-embed-text`.                         |
| PDF dodaje 0 fragmentów   | To prawdopodobnie skan (obraz). Ten projekt czyta tylko tekst z PDF. |
| Lista modeli pusta        | Pobierz model (`ollama pull gemma3:4b`) i kliknij **↻**.             |
| Chcę zacząć od zera       | Usuń folder `data/` i uruchom ponownie.                              |

## Parametry do strojenia (config.py)

- `CHUNK_SIZE` / `CHUNK_OVERLAP` — rozmiar fragmentów i ich zachodzenie.
- `TOP_K` — ile fragmentów trafia do kontekstu (więcej = pełniejszy kontekst, ale wolniej).
- `LLM_TEMPERATURE` — 0 = konkretnie i powtarzalnie, wyżej = bardziej kreatywnie.
