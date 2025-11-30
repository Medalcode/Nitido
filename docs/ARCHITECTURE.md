# Arquitectura de Nítido

## Visión general

Nítido es un sistema de tres capas:

```
[Chrome Extension] ───→ [FastAPI Backend] ───→ [LLM (Gemini/Groq)]
                            │
                            ├── [ChromaDB / Corpus Legal]
                            ├── [Risk Detector (reglas)]
                            └── [PostgreSQL / SQLite]
```

## Backend (FastAPI)

- `POST /api/v1/analizar` — analiza texto legal
- `POST /api/v1/analizar/pdf` — analiza PDF
- `GET /health` — health check

### Servicios

| Servicio | Responsabilidad |
|----------|----------------|
| `parser.py` | Extracción de texto (PDF, raw) y detección de cláusulas |
| `risk_detector.py` | Reglas de cláusulas abusivas + patrones de riesgo |
| `corpus.py` | Carga y consulta del corpus legal chileno |
| `summarizer.py` | Conexión con LLM para resumen y análisis |

### Flujo de análisis

1. Recibe texto o PDF
2. Extrae cláusulas individuales (parser)
3. Evalúa cada cláusula contra reglas de riesgo (risk_detector)
4. Envía resumen al LLM con contexto legal chileno
5. Compila respuesta con resumen + cláusulas + recomendaciones

## Chrome Extension

- Detecta automáticamente páginas con términos legales
- Permite seleccionar texto y analizarlo
- Muestra resultados en el popup con código de colores

## Roadmap

### Fase 1 (MVP) — Diciembre 2025
- [x] Backend FastAPI con endpoints básicos
- [x] Parser de PDF y texto
- [x] Risk detector con reglas
- [x] Integración con Gemini
- [x] Landing page web
- [ ] Chrome extension funcional
- [ ] Despliegue en producción

### Fase 2 — Enero 2026
- [ ] Corpus RAG completo (Ley del Consumidor, SERNAC)
- [ ] Fine-tuning del LLM con documentos legales chilenos
- [ ] Dashboard de estadísticas
- [ ] Autenticación de usuarios

### Fase 3 — Febrero 2026
- [ ] Comparador de documentos
- [ ] Historial de análisis
- [ ] Modo oscuro claro
- [ ] API pública para terceros
