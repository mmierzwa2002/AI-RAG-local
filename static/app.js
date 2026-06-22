const $ = (id) => document.getElementById(id);

// --- elementy DOM ---
const statusDot   = $("statusDot");
const statusText  = $("statusText");
const dropzone    = $("dropzone");
const fileInput   = $("fileInput");
const browseBtn   = $("browseBtn");
const uploadStatus= $("uploadStatus");
const docList     = $("docList");
const chunkCount  = $("chunkCount");
const modelSelect = $("modelSelect");
const refreshBtn  = $("refreshModels");
const topK        = $("topK");
const askForm     = $("askForm");
const question    = $("question");
const askBtn      = $("askBtn");
const answerArea  = $("answerArea");
const sources     = $("sources");
const sourceCards = $("sourceCards");

// Inicjalizacja
document.addEventListener("DOMContentLoaded", () => {
  refreshStatus();
  loadModels();
  loadDocuments();
  // odswiezaj stan Ollamy co 15 s
  setInterval(refreshStatus, 15000);
});

// Stan serwera Ollama
async function refreshStatus() {
  try {
    const r = await fetch("/api/status");
    const d = await r.json();
    if (d.ollama) {
      statusDot.className = "status-dot online";
      statusText.textContent = "ollama online";
    } else {
      statusDot.className = "status-dot offline";
      statusText.textContent = "ollama offline";
    }
    chunkCount.textContent = `${d.chunks} frag.`;
  } catch {
    statusDot.className = "status-dot offline";
    statusText.textContent = "brak polaczenia";
  }
}

// Lista modeli (wybor w interfejsie)
async function loadModels() {
  refreshBtn.classList.add("spinning");
  try {
    const r = await fetch("/api/models");
    const d = await r.json();
    modelSelect.innerHTML = "";

    if (!d.models.length) {
      const opt = document.createElement("option");
      opt.textContent = "brak modeli — pobierz je w Ollamie";
      opt.disabled = true;
      modelSelect.appendChild(opt);
      return;
    }

    d.models.forEach((name) => {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      modelSelect.appendChild(opt);
    });

    // ustaw model domyslny, jesli jest zainstalowany
    if (d.models.includes(d.default)) {
      modelSelect.value = d.default;
    }
  } catch {
    modelSelect.innerHTML = "<option disabled>nie udalo sie pobrac modeli</option>";
  } finally {
    setTimeout(() => refreshBtn.classList.remove("spinning"), 400);
  }
}

refreshBtn.addEventListener("click", loadModels);

// Lista dokumentow w bazie
async function loadDocuments() {
  try {
    const r = await fetch("/api/documents");
    const d = await r.json();
    renderDocuments(d.documents);
  } catch {
    docList.innerHTML = '<li class="doc-empty">Nie udalo sie wczytac listy.</li>';
  }
}

function renderDocuments(docs) {
  if (!docs.length) {
    docList.innerHTML = '<li class="doc-empty">Baza jest pusta.<br>Dodaj pierwszy dokument.</li>';
    return;
  }
  docList.innerHTML = "";
  docs.forEach((doc) => {
    const li = document.createElement("li");
    li.className = "doc-item";
    li.innerHTML = `
      <span class="doc-icon">▸</span>
      <span class="doc-info">
        <span class="doc-name" title="${escapeHtml(doc.name)}">${escapeHtml(doc.name)}</span>
        <span class="doc-meta">${doc.chunks} frag.</span>
      </span>
      <button class="doc-del" title="Usun z bazy">×</button>`;
    li.querySelector(".doc-del").addEventListener("click", () => deleteDocument(doc.name));
    docList.appendChild(li);
  });
}

async function deleteDocument(name) {
  if (!confirm(`Usunac "${name}" z bazy wiedzy?`)) return;
  await fetch("/api/documents/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  loadDocuments();
  refreshStatus();
}

// Wgrywanie dokumentow (klik + drag & drop)
browseBtn.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("click", (e) => {
  if (e.target === browseBtn) return; // przycisk obsluguje sie sam
  fileInput.click();
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) uploadFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => {
  if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
});

async function uploadFile(file) {
  showUpload("working", `Przetwarzanie „${file.name}”…`, true);

  const form = new FormData();
  form.append("file", file);

  try {
    const r = await fetch("/api/upload", { method: "POST", body: form });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || "Nieznany blad.");

    showUpload("ok", `Dodano „${d.name}” — ${d.chunks} fragmentow.`);
    loadDocuments();
    refreshStatus();
  } catch (err) {
    showUpload("error", err.message);
  } finally {
    fileInput.value = "";
  }
}

function showUpload(type, msg, withSpinner = false) {
  uploadStatus.hidden = false;
  uploadStatus.className = `upload-status ${type}`;
  uploadStatus.innerHTML = (withSpinner ? '<span class="spinner"></span>' : "") + escapeHtml(msg);
  if (type !== "working") {
    setTimeout(() => { uploadStatus.hidden = true; }, 5000);
  }
}

// Zadawanie pytan
askForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = question.value.trim();
  if (!q) return;

  setAsking(true);
  showThinking();
  sources.hidden = true;

  try {
    const r = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: q,
        model: modelSelect.value,
        top_k: parseInt(topK.value) || 4,
      }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || "Nieznany blad.");

    showAnswer(d);
    renderSources(d.sources);
  } catch (err) {
    showError(err.message);
  } finally {
    setAsking(false);
  }
});

function setAsking(busy) {
  askBtn.disabled = busy;
  askBtn.textContent = busy ? "Szukam…" : "Zapytaj";
}

function showThinking() {
  answerArea.innerHTML = `
    <div class="thinking">
      <span class="thinking-dots"><span></span><span></span><span></span></span>
      Przeszukuje baze i pytam model…
    </div>`;
}

function showAnswer(d) {
  answerArea.innerHTML = `
    <div class="answer-text">${renderMarkdown(d.answer)}</div>
    <div class="answer-meta">
      <span>model: ${escapeHtml(d.model)}</span>
      <span>zrodel: ${d.sources.length}</span>
    </div>`;
}

// Model czesto formatuje odpowiedzi markdownem (**pogrubienia**, listy, naglowki).
// Zamieniamy najczestsze konstrukcje na HTML — bez zewnetrznych bibliotek, bo
// aplikacja dziala w pelni lokalnie. Bezpieczenstwo: cala tresc najpierw
// escapujemy (odpowiedz pochodzi z modelu czytajacego pliki uzytkownika),
// formatowanie nakladamy dopiero na zescapowany tekst.
function renderMarkdown(src) {
  const esc = (s) =>
    s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

  // bloki kodu ``` ... ``` odkladamy na bok, zeby nie ruszylo ich formatowanie
  const blocks = [];
  src = String(src ?? "").replace(/```[\w-]*\n?([\s\S]*?)```/g, (_, code) => {
    blocks.push(code.replace(/\n$/, ""));
    return `@@CB${blocks.length - 1}@@`;
  });

  const inline = (t) =>
    esc(t)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/__([^_]+)__/g, "<strong>$1</strong>")
      .replace(/(^|[^*])\*(?!\s)([^*\n]+?)\*/g, "$1<em>$2</em>")
      .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener">$1</a>');

  const out = [];
  let list = null;          // "ul" | "ol" | null
  let para = [];
  const flushPara = () => {
    if (para.length) { out.push(`<p>${para.map(inline).join("<br>")}</p>`); para = []; }
  };
  const closeList = () => { if (list) { out.push(`</${list}>`); list = null; } };

  for (const raw of src.split("\n")) {
    const line = raw.trim();

    if (!line) { flushPara(); closeList(); continue; }

    const code = line.match(/^@@CB(\d+)@@$/);
    if (code) {
      flushPara(); closeList();
      out.push(`<pre><code>${esc(blocks[+code[1]])}</code></pre>`);
      continue;
    }

    const h = line.match(/^(#{1,4})\s+(.+)$/);
    if (h) {
      flushPara(); closeList();
      const lvl = Math.min(6, h[1].length + 2);
      out.push(`<h${lvl}>${inline(h[2])}</h${lvl}>`);
      continue;
    }

    const ul = line.match(/^[-*+]\s+(.+)$/);
    if (ul) {
      flushPara();
      if (list !== "ul") { closeList(); out.push("<ul>"); list = "ul"; }
      out.push(`<li>${inline(ul[1])}</li>`);
      continue;
    }

    const ol = line.match(/^\d+[.)]\s+(.+)$/);
    if (ol) {
      flushPara();
      if (list !== "ol") { closeList(); out.push("<ol>"); list = "ol"; }
      out.push(`<li>${inline(ol[1])}</li>`);
      continue;
    }

    closeList();
    para.push(line);
  }
  flushPara();
  closeList();
  return out.join("\n");
}

function showError(msg) {
  answerArea.innerHTML = `<div class="error-box">${escapeHtml(msg)}</div>`;
  sources.hidden = true;
}

// --- karty zrodel (element rozpoznawczy interfejsu) ---
function renderSources(items) {
  if (!items || !items.length) {
    sources.hidden = true;
    return;
  }
  sourceCards.innerHTML = "";
  sources.hidden = false; // odslaniamy PRZED pomiarem wysokosci, inaczej wymiary = 0

  items.forEach((s, i) => {
    const pct = Math.max(0, Math.min(100, Math.round(s.score * 100)));
    const card = document.createElement("div");
    card.className = "source-card";
    card.innerHTML = `
      <div class="source-top">
        <span class="source-rank">${i + 1}</span>
        <span class="source-doc" title="${escapeHtml(s.doc_name)}">${escapeHtml(s.doc_name)}</span>
      </div>
      <div class="score">
        <div class="score-bar"><div class="score-fill" style="width:${pct}%"></div></div>
        <span class="score-label">trafnosc ${pct}%</span>
      </div>
      <div class="source-text">${escapeHtml(s.text)}</div>
      <div class="source-toggle">rozwiń ▾</div>`;
    sourceCards.appendChild(card);

    const textEl = card.querySelector(".source-text");
    const toggleEl = card.querySelector(".source-toggle");

    // najpierw nakladamy limit wysokosci, potem mierzymy czy tekst sie miesci
    card.classList.add("is-truncated");
    if (textEl.scrollHeight > textEl.clientHeight + 2) {
      // fragment faktycznie przyciety -> rozwijalny po kliknieciu
      card.addEventListener("click", () => {
        const expanded = card.classList.toggle("expanded");
        toggleEl.textContent = expanded ? "zwiń ▴" : "rozwiń ▾";
      });
    } else {
      // miesci sie w calosci -> bez limitu, bez fade, bez przycisku
      card.classList.remove("is-truncated");
    }
  });
}

// Pomocnicze
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}