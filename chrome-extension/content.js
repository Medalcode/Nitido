// Nitido - content script
// Detecta si la página actual contiene textos legales (términos, contratos, etc.)

const keywords = [
  "términos y condiciones", "política de privacidad", "contrato",
  "aviso legal", "cláusula", "condiciones generales",
];

const bodyText = document.body.innerText.toLowerCase();
const hasLegal = keywords.some((k) => bodyText.includes(k));

if (hasLegal) {
  chrome.runtime.sendMessage({
    type: "LEGAL_DETECTED",
    url: window.location.href,
  });
}
