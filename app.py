"""
Aplikacja Flask - warstwa webowa systemu RAG.

Endpointy:
  GET  /                       -> strona glowna (interfejs)
  GET  /api/status             -> czy Ollama dziala + liczba fragmentow w bazie
  GET  /api/models             -> lista zainstalowanych modeli + model domyslny
  GET  /api/documents          -> lista dokumentow w bazie
  POST /api/upload             -> wgranie i zaindeksowanie pliku
  POST /api/documents/delete   -> usuniecie dokumentu z bazy
  POST /api/query              -> zadanie pytania (retrieval + generacja)
"""
import os
import traceback

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

import config
from rag import RagEngine

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_MB * 1024 * 1024

# katalogi na dane tworzymy przy starcie
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.STORE_DIR, exist_ok=True)

# jeden silnik RAG na cala aplikacje (laduje baze z dysku)
engine = RagEngine()


def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify({
        "ollama": engine.client.is_available(),
        "chunks": engine.store.total_chunks(),
        "embedding_model": config.EMBEDDING_MODEL,
    })


@app.route("/api/models")
def models():
    """Lista modeli do wyboru w interfejsie - tylko te, ktore potrafia generowac
    tekst (modele embeddingowe jak nomic-embed-text czy bge-m3 sa pomijane)."""
    try:
        installed = engine.client.list_models()
    except Exception:
        installed = []
    chat_models = [m for m in installed if engine.client.can_generate(m)]
    return jsonify({
        "models": chat_models,
        "default": config.DEFAULT_LLM_MODEL,
    })


@app.route("/api/documents")
def documents():
    return jsonify({"documents": engine.store.list_documents()})


@app.route("/api/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Brak pliku w zadaniu."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nie wybrano pliku."}), 400

    if not allowed_file(file.filename):
        allowed = ", ".join(sorted(config.ALLOWED_EXTENSIONS))
        return jsonify({"error": f"Nieobslugiwany typ pliku. Dozwolone: {allowed}"}), 400

    if not engine.client.is_available():
        return jsonify({"error": "Ollama nie odpowiada. Uruchom serwer Ollama i sprobuj ponownie."}), 503

    filename = secure_filename(file.filename)
    save_path = os.path.join(config.UPLOAD_DIR, filename)
    file.save(save_path)

    try:
        info = engine.add_document(save_path, filename)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Blad przetwarzania: {e}"}), 500

    return jsonify({
        "ok": True,
        "name": filename,
        "chunks": info["chunks"],
        "chars": info["chars"],
    })


@app.route("/api/documents/delete", methods=["POST"])
def delete_document():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "Brak nazwy dokumentu."}), 400

    removed = engine.store.delete_document(name)
    # usun tez oryginalny plik (jesli istnieje)
    path = os.path.join(config.UPLOAD_DIR, name)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass

    return jsonify({"ok": removed})


@app.route("/api/query", methods=["POST"])
def query():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    model = data.get("model") or config.DEFAULT_LLM_MODEL
    top_k = int(data.get("top_k") or config.TOP_K)

    if not question:
        return jsonify({"error": "Pytanie jest puste."}), 400

    if not engine.client.is_available():
        return jsonify({"error": "Ollama nie odpowiada. Uruchom serwer Ollama i sprobuj ponownie."}), 503

    try:
        result = engine.query(question, model=model, top_k=top_k)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Blad generowania: {e}"}), 500

    return jsonify(result)


if __name__ == "__main__":
    print("=" * 60)
    print("  System RAG - http://localhost:5000")
    print(f"  Ollama:           {config.OLLAMA_URL}")
    print(f"  Model domyslny:   {config.DEFAULT_LLM_MODEL}")
    print(f"  Model embeddingu: {config.EMBEDDING_MODEL}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
