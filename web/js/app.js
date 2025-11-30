const API_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
  ? "http://localhost:8000/api/v1"
  : "/api/v1";

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const input = document.getElementById("input");
const analyzeBtn = document.getElementById("analyzeBtn");
const result = document.getElementById("result");
const loading = document.getElementById("loading");

let selectedFile = null;

dropZone.addEventListener("click", () => fileInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].type === "application/pdf") {
    handleFile(files[0]);
  }
});

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFile(e.target.files[0]);
  }
});

function handleFile(file) {
  selectedFile = file;
  dropZone.innerHTML = `
    <div class="drop-content">
      <div class="drop-icon">✅</div>
      <p class="file-selected">${file.name}</p>
      <p class="drop-hint">${(file.size / 1024).toFixed(1)} KB — Haz clic para cambiar</p>
    </div>
  `;
}

analyzeBtn.addEventListener("click", async () => {
  if (selectedFile) {
    await analizarPDF(selectedFile);
  } else {
    const text = input.value.trim();
    if (!text || text.length < 10) return;
    await analizarTexto(text);
  }
});

async function analizarTexto(text) {
  loading.style.display = "block";
  analyzeBtn.disabled = true;
  result.innerHTML = "";

  try {
    const res = await fetch(`${API_URL}/analizar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contenido: text }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `Error ${res.status}`);
    }
    renderResult(await res.json());
  } catch (err) {
    showError(err.message);
  } finally {
    loading.style.display = "none";
    analyzeBtn.disabled = false;
  }
}

async function analizarPDF(file) {
  if (file.size > 10 * 1024 * 1024) {
    showError("El PDF no puede superar los 10 MB");
    return;
  }

  loading.style.display = "block";
  analyzeBtn.disabled = true;
  result.innerHTML = "";

  try {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_URL}/analizar/pdf`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `Error ${res.status}`);
    }
    renderResult(await res.json());
  } catch (err) {
    showError(err.message);
  } finally {
    loading.style.display = "none";
    analyzeBtn.disabled = false;
  }
}

function renderResult(data) {
  let html = "";

  html += `<div class="resumen-section"><h3>📝 Resumen</h3><p>${data.resumen}</p></div>`;

  const maxScore = Math.max(data.total_clausulas || 1, 1);
  const pct = Math.round((data.puntaje_riesgo / maxScore) * 100);
  const scoreColor = pct > 50 ? "#ef4444" : pct > 20 ? "#f97316" : "#22c55e";

  html += `<div class="score-section">
    <span class="number" style="color:${scoreColor}">${data.puntaje_riesgo}</span>
    <span class="label">de ${data.total_clausulas} cláusulas presentan riesgo</span>
  </div>`;

  if (data.clausulas.length > 0) {
    html += `<div class="clausulas-section"><h3>⚖️ Cláusulas analizadas</h3>`;
    for (const c of data.clausulas) {
      const tagClass = `tag-${c.riesgo}`;
      html += `<div class="clausula ${c.riesgo}">
        <span class="tag ${tagClass}">${c.riesgo}</span>
        <div>${c.texto_simple || c.texto_original}</div>
        ${c.fundamento_legal ? `<div class="fundamento">${c.fundamento_legal}</div>` : ""}
      </div>`;
    }
    html += `</div>`;
  }

  if (data.glosario && Object.keys(data.glosario).length > 0) {
    html += `<details class="glosario-box"><summary>📖 Glosario (${Object.keys(data.glosario).length} términos)</summary><dl>`;
    for (const [term, def] of Object.entries(data.glosario)) {
      html += `<dt>${term}</dt><dd>${def}</dd>`;
    }
    html += `</dl></details>`;
  }

  if (data.recomendaciones && data.recomendaciones.length > 0) {
    html += `<div class="recomendaciones-box"><h3>✅ Recomendaciones</h3><ol>`;
    for (const r of data.recomendaciones) {
      html += `<li>${r}</li>`;
    }
    html += `</ol></div>`;
  }

  result.innerHTML = html;
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showError(msg) {
  result.innerHTML = `<div style="color:#ef4444;text-align:center;padding:20px;background:#7f1d1d1a;border-radius:8px;border:1px solid #7f1d1d">${msg}</div>`;
}
