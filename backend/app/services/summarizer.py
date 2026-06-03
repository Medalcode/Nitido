import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)

PROMPT_RESUMEN = """Eres un asistente experto en simplificar documentos legales chilenos.

DOCUMENTO:
{contenido}

CONTEXTO LEGAL DE REFERENCIA (Leyes y Jurisprudencia):
{contexto_legal}

Debes devolver SOLO un objeto JSON válido con esta estructura exacta, sin markdown ni explicaciones:
{{
  "resumen": "explicación en español simple de 3-4 párrafos",
  "glosario": {{"término legal": "significado simple", ...}},
  "recomendaciones": ["recomendación 1", "recomendación 2", ...]
}}

Usa español ciudadano. Piensa que le explicas a un familiar. Basa tu análisis en la Ley 19.496 y el contexto entregado."""


class LegalSummarizer:
    def __init__(self, gemini_key: str, groq_key: str = ""):
        self.gemini_key = gemini_key
        self.groq_key = groq_key

    async def resumir(self, contenido: str, contexto_legal: str = "") -> dict:
        contenido = contenido[:settings.max_document_length]

        if settings.mock_mode:
            return self._mock_response(contenido)

        if self.gemini_key:
            try:
                return await self._resumir_con_gemini(contenido, contexto_legal)
            except Exception as e:
                logger.warning("Gemini falló, intentando Groq: %s", e)

        if self.groq_key:
            try:
                return await self._resumir_con_groq(contenido, contexto_legal)
            except Exception as e:
                logger.warning("Groq también falló: %s", e)

        return self._mock_response(contenido)

    async def _resumir_con_gemini(self, contenido: str, contexto_legal: str) -> dict:
        from google import genai

        client = genai.Client(api_key=self.gemini_key)
        prompt = PROMPT_RESUMEN.format(contenido=contenido, contexto_legal=contexto_legal or "No hay contexto adicional.")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return self._parsear_respuesta(response.text)

    async def _resumir_con_groq(self, contenido: str, contexto_legal: str) -> dict:
        import httpx

        prompt = PROMPT_RESUMEN.format(contenido=contenido, contexto_legal=contexto_legal or "No hay contexto adicional.")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            return self._parsear_respuesta(resp.json()["choices"][0]["message"]["content"])

    def _parsear_respuesta(self, texto: str) -> dict:
        texto = texto.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(texto)
        return {
            "resumen": data.get("resumen", ""),
            "glosario": data.get("glosario", {}),
            "recomendaciones": data.get("recomendaciones", []),
        }

    def _mock_response(self, contenido: str) -> dict:
        preview = contenido[:200].replace("\n", " ")
        return {
            "resumen": (
                f"**Modo simulación** — No hay API key configurada.\n\n"
                f"Este documento de {len(contenido)} caracteres trata sobre: "
                f"\"{preview}...\"\n\n"
                f"Con una API key (Gemini o Groq), Nítido generaría un resumen, "
                f"glosario y recomendaciones basados en la Ley 19.496."
            ),
            "glosario": {
                "arrendador": "Dueño de la propiedad que arrienda",
                "arrendatario": "Persona que arrienda",
                "usufructo": "Derecho a usar algo que es de otro",
                "precario": "Ocupación sin contrato ni pago",
                "fianza": "Garantía de que alguien cumplirá",
            },
            "recomendaciones": [
                "Configura GEMINI_API_KEY o GROQ_API_KEY en .env para obtener análisis real.",
                "Revisa siempre las cláusulas marcadas en rojo antes de firmar.",
                "Si tienes dudas, consulta con un abogado.",
            ],
        }
