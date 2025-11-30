import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_analizar_documento_valido(client):
    response = await client.post(
        "/api/v1/analizar",
        json={"contenido": "Artículo 1°.- El arrendador entrega el inmueble. El cliente renuncia a todos sus derechos legales."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "resumen" in data
    assert "clausulas" in data
    assert "puntaje_riesgo" in data
    assert "recomendaciones" in data


@pytest.mark.asyncio
async def test_analizar_documento_demasiado_corto(client):
    response = await client.post(
        "/api/v1/analizar",
        json={"contenido": "corto"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analizar_documento_con_tipo(client):
    response = await client.post(
        "/api/v1/analizar",
        json={
            "contenido": "Cláusula Primera: Objeto del contrato de arriendo.",
            "tipo_documento": "contrato",
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analizar_pdf_sin_archivo(client):
    response = await client.post("/api/v1/analizar/pdf")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_corpus_endpoint(client):
    response = await client.get("/api/v1/corpus")
    assert response.status_code == 200
    data = response.json()
    assert "documentos" in data


@pytest.mark.asyncio
async def test_analizar_documento_estructura_respuesta(client):
    response = await client.post(
        "/api/v1/analizar",
        json={"contenido": "Artículo 1.- El plazo del contrato es de 12 meses. Artículo 2.- El arrendatario pagará $500.000 mensuales."},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["clausulas"], list)
    assert isinstance(data["glosario"], dict)
    assert isinstance(data["recomendaciones"], list)
    assert isinstance(data["puntaje_riesgo"], int)
    assert isinstance(data["total_clausulas"], int)
