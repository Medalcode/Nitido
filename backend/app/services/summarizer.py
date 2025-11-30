class LegalSummarizer:
    PROMPT_RESUMEN = """
Eres un asistente legal especializado en simplificar documentos legales chilenos.

Documento a analizar:
{contenido}

Genera:
1. RESUMEN: Explica en 3-4 párrafos de español simple y ciudadano qué dice este documento.
   Usa frases cortas, evita tecnicismos. Piensa que se lo explicas a un familiar.

2. GLOSARIO: Lista las palabras o frases legales complejas y su significado en español simple.

3. RECOMENDACIONES: Lista numerada de acciones recomendadas antes de firmar este documento.
"""

    PROMPT_ANALISIS_CLAUSULAS = """
Analiza estas cláusulas de un documento legal chileno:

{clausulas}

Para cada una, determina:
- riesgo: bajo/medio/alto/crítico
- fundamento legal: qué ley chilena podría estar violando
- sugerencia: qué hacer al respecto

Basate en la Ley N° 19.496 (Protección al Consumidor) y normativa SERNAC.
"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def resumir(self, contenido: str) -> dict:
        from google import genai
        client = genai.Client(api_key=self.api_key)
        prompt = self.PROMPT_RESUMEN.format(contenido=contenido[:15000])
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return {"resumen": response.text}
