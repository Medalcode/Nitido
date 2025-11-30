import pytest
from app.services.summarizer import LegalSummarizer


@pytest.mark.asyncio
async def test_mock_response_sin_api_key():
    summarizer = LegalSummarizer(gemini_key="", groq_key="")
    resultado = await summarizer.resumir("Documento de prueba sobre contrato de arriendo.")
    assert "resumen" in resultado
    assert "mock" in resultado["resumen"].lower() or "Modo simulación" in resultado["resumen"]


@pytest.mark.asyncio
async def test_mock_response_incluye_glosario():
    summarizer = LegalSummarizer(gemini_key="", groq_key="")
    resultado = await summarizer.resumir("Test")
    assert "glosario" in resultado
    assert isinstance(resultado["glosario"], dict)
    assert len(resultado["glosario"]) > 0


@pytest.mark.asyncio
async def test_mock_response_incluye_recomendaciones():
    summarizer = LegalSummarizer(gemini_key="", groq_key="")
    resultado = await summarizer.resumir("Test")
    assert "recomendaciones" in resultado
    assert isinstance(resultado["recomendaciones"], list)


def test_parsear_respuesta_json():
    summarizer = LegalSummarizer(gemini_key="")
    respuesta = '{"resumen": "Texto simple", "glosario": {"a": "b"}, "recomendaciones": ["c"]}'
    resultado = summarizer._parsear_respuesta(respuesta)
    assert resultado["resumen"] == "Texto simple"
    assert resultado["glosario"]["a"] == "b"
    assert "c" in resultado["recomendaciones"]


def test_parsear_respuesta_con_markdown():
    summarizer = LegalSummarizer(gemini_key="")
    respuesta = '```json\n{"resumen": "Test", "glosario": {}, "recomendaciones": []}\n```'
    resultado = summarizer._parsear_respuesta(respuesta)
    assert resultado["resumen"] == "Test"


def test_parsear_respuesta_campos_faltantes():
    summarizer = LegalSummarizer(gemini_key="")
    resultado = summarizer._parsear_respuesta('{"resumen": "Solo resumen"}')
    assert resultado["resumen"] == "Solo resumen"
    assert resultado["glosario"] == {}
    assert resultado["recomendaciones"] == []
