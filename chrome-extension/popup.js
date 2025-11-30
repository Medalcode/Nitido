document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const input = document.getElementById("input").value.trim();
  if (!input) return;

  const resultDiv = document.getElementById("result");
  const loading = document.getElementById("loading");
  const btn = document.getElementById("analyzeBtn");

  loading.style.display = "block";
  btn.disabled = true;
  resultDiv.innerHTML = "";

  chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
    try {
      const response = await fetch("https://api.nitido.cl/api/v1/analizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contenido: input }),
      });

      if (!response.ok) throw new Error("Error al analizar");

      const data = await response.json();
      mostrarResultados(data);
    } catch (err) {
      resultDiv.innerHTML = `<div class="error">${err.message}</div>`;
    } finally {
      loading.style.display = "none";
      btn.disabled = false;
    }
  });
});

function mostrarResultados(data) {
  const resultDiv = document.getElementById("result");
  let html = `<h3 style="margin-bottom:8px;color:#2dd4bf">Resumen</h3><p style="margin-bottom:16px;font-size:13px">${data.resumen}</p>`;
  html += `<h3 style="margin-bottom:8px;color:#2dd4bf">Cláusulas (${data.clausulas.length})</h3>`;
  data.clausulas.forEach((c) => {
    html += `<div class="clausula ${c.riesgo}"><strong>${c.riesgo.toUpperCase()}</strong>: ${c.texto_simple || c.texto_original}</div>`;
  });
  if (data.recomendaciones.length) {
    html += `<h3 style="margin:16px 0 8px;color:#2dd4bf">Recomendaciones</h3><ul style="font-size:13px;padding-left:16px">`;
    data.recomendaciones.forEach((r) => (html += `<li style="margin-bottom:4px">${r}</li>`));
    html += "</ul>";
  }
  resultDiv.innerHTML = html;
}
