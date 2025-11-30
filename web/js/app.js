const API_URL = "http://localhost:8000/api/v1";

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("analyzeBtn");
  const input = document.getElementById("input");
  const result = document.getElementById("result");
  const loading = document.getElementById("loading");

  btn.addEventListener("click", async () => {
    const text = input.value.trim();
    if (!text || text.length < 10) return;

    loading.style.display = "block";
    btn.disabled = true;
    result.innerHTML = "";

    try {
      const res = await fetch(`${API_URL}/analizar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contenido: text }),
      });
      if (!res.ok) throw new Error("Error del servidor");
      const data = await res.json();
      renderResult(data);
    } catch (err) {
      result.innerHTML = `<div style="color:#ef4444;text-align:center">${err.message}</div>`;
    } finally {
      loading.style.display = "none";
      btn.disabled = false;
    }
  });
});

function renderResult(data) {
  let html = "";
  html += `<div class="resumen-section"><h3 style="color:#2dd4bf;margin-bottom:8px">Resumen</h3><p>${data.resumen}</p></div>`;
  html += `<h3 style="color:#2dd4bf;margin:16px 0 12px">Cláusulas (${data.clausulas.length})</h3>`;
  data.clausulas.forEach((c) => {
    const nivel = c.riesgo;
    html += `<div class="clausula ${nivel}"><strong>${nivel.toUpperCase()}</strong> ${c.texto_original}</div>`;
  });
  if (data.recomendaciones?.length) {
    html += `<h3 style="color:#2dd4bf;margin:16px 0 8px">Recomendaciones</h3><ul style="padding-left:20px">`;
    data.recomendaciones.forEach((r) => (html += `<li style="margin-bottom:4px">${r}</li>`));
    html += "</ul>";
  }
  document.getElementById("result").innerHTML = html;
}
