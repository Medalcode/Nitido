const API_URL = "http://localhost:8000/api/v1";

const input = document.getElementById("input");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultDiv = document.getElementById("result");
const loading = document.getElementById("loading");
const getPageBtn = document.getElementById("getPageBtn");
const clearBtn = document.getElementById("clearBtn");

analyzeBtn.addEventListener("click", analizar);
clearBtn.addEventListener("click", () => {
  input.value = "";
  resultDiv.innerHTML = "";
});

getPageBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      func: () => {
        const paragraphs = document.querySelectorAll("p, li, td, th, span, div");
        let text = "";
        for (const el of paragraphs) {
          const t = el.innerText.trim();
          if (t.length > 40) text += t + "\n";
        }
        return text.substring(0, 15000);
      },
    },
    (results) => {
      if (results && results[0] && results[0].result) {
        input.value = results[0].result;
      }
    }
  );
});

async function analizar() {
  const text = input.value.trim();
  if (!text || text.length < 10) return;

  loading.style.display = "block";
  analyzeBtn.disabled = true;
  resultDiv.innerHTML = "";

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

    const data = await res.json();
    renderResult(data);
  } catch (err) {
    resultDiv.innerHTML = `<div class="error">${err.message}</div>`;
  } finally {
    loading.style.display = "none";
    analyzeBtn.disabled = false;
  }
}

function renderResult(data) {
  let html = "";

  html += `<div class="resumen-box"><h3>📝 Resumen</h3><p>${data.resumen}</p></div>`;

  const maxScore = Math.max(data.total_clausulas, 1);
  const pct = Math.round((data.puntaje_riesgo / maxScore) * 100);
  const barColor = pct > 50 ? "#ef4444" : pct > 20 ? "#f97316" : "#22c55e";
  html += `<div class="score-bar">
    <span class="label" style="color:${barColor}">${data.puntaje_riesgo}/${data.total_clausulas}</span>
    <div class="bar"><div class="fill" style="width:${pct}%;background:${barColor}"></div></div>
    <span style="font-size:11px;color:#64748b">cláusulas con riesgo</span>
  </div>`;

  if (data.clausulas.length > 0) {
    html += `<div style="margin-top:4px;font-size:11px;color:#64748b;margin-bottom:8px">Cláusulas detectadas:</div>`;
    for (const c of data.clausulas) {
      const tagClass = `tag-${c.riesgo}`;
      html += `<div class="clausula ${c.riesgo}">
        <span class="tag ${tagClass}">${c.riesgo}</span>
        <div>${c.texto_simple || c.texto_original}</div>
        ${c.fundamento_legal ? `<div class="fundamento">${c.fundamento_legal}</div>` : ""}
      </div>`;
    }
  }

  if (data.glosario && Object.keys(data.glosario).length > 0) {
    html += `<button class="glosario-toggle" onclick="toggleGlosario()">📖 Ver glosario (${Object.keys(data.glosario).length} términos)</button>`;
    html += `<div class="glosario" id="glosario"><dl>`;
    for (const [term, def] of Object.entries(data.glosario)) {
      html += `<dt>${term}</dt><dd>${def}</dd>`;
    }
    html += `</dl></div>`;
  }

  if (data.recomendaciones && data.recomendaciones.length > 0) {
    html += `<div class="recomendaciones"><h3>✅ Recomendaciones</h3><ul>`;
    for (const r of data.recomendaciones) {
      html += `<li>${r}</li>`;
    }
    html += `</ul></div>`;
  }

  resultDiv.innerHTML = html;
}

function toggleGlosario() {
  const el = document.getElementById("glosario");
  el.style.display = el.style.display === "block" ? "none" : "block";
}
