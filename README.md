# Nítido

**Descifra documentos legales al español simple.**

Nítido es una plataforma que usa inteligencia artificial para traducir documentos legales (contratos, términos y condiciones, cartas bancarias, pólizas de Isapre) a lenguaje claro y ciudadano. Escanea cláusulas abusivas, calcula riesgos y te dice —en simple— qué estás firmando.

## Problema

En Chile, la mayoría de los documentos legales están escritos en un lenguaje inaccesible para el ciudadano común. Contratos de arriendo, tarjetas de crédito, cuentas bancarias, Isapres, fondos mutuos —todos usan legalese que oculta cláusulas abusivas, costos ocultos y riesgos.

Las consecuencias:
- Familias que firman sin entender
- Cláusulas abusivas que pasan desapercibidas
- Asimetría de información entre empresas y consumidores
- Personas que aceptan condiciones que jamás aceptarían si las entendieran

## Solución

Nítido recibe un documento legal (PDF, texto, URL) y devuelve:

1. **Resumen TL;DR** — qué dice el documento en 3 párrafos de español simple
2. **Cláusulas de riesgo** — qué frases son abusivas, incompletas o peligrosas, basado en la Ley del Consumidor y jurisprudencia SERNAC
3. **Diccionario legal** — cada término complejo traducido al español ciudadano
4. **Comparador** — cómo se compara este documento contra estándares de la industria
5. **Recomendaciones** — qué pedir que cambien antes de firmar

## Stack

| Componente | Tecnología |
|------------|-----------|
| Backend | Python 3.12 + FastAPI |
| Frontend | HTML + CSS + Vanilla JS (luego React) |
| Extensión | Chrome Extension (Manifest V3) |
| LLM | Google Gemini + Groq |
| Base de datos | PostgreSQL (Planificado) |
| Vector store | ChromaDB (Integrado para Corpus legal chileno y RAG) |
| Contenedores | Docker + docker-compose |
| Despliegue | Vercel (API) + Chrome Web Store |

## Estructura del proyecto

```
Nitido/
├── backend/           # API REST (FastAPI + LLM + RAG)
│   ├── app/
│   │   ├── services/  # parser, summarizer, risk_detector, corpus
│   │   ├── models/    # Pydantic schemas
│   │   ├── api/       # Endpoints REST
│   │   └── reglas.json # Motor de reglas de riesgo (Ley 19.496)
│   └── data/          # Volumen montado para ChromaDB y recursos
├── chrome-extension/  # Extensión para Chrome
├── web/               # Landing page + dashboard web
├── data/corpus/       # Leyes, jurisprudencia, cláusulas
└── docs/              # Documentación técnica
```

## Licencia

MIT
