import pytest
from app.services.risk_detector import RiskDetector


def test_riesgo_bajo():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": "El plazo del contrato es de 12 meses."}])
    assert resultado[0]["riesgo"] == "bajo"
    assert resultado[0]["fundamento_legal"] is None


def test_riesgo_alto_renuncia_derechos():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": "El cliente renuncia a todos sus derechos legales."}])
    assert resultado[0]["riesgo"] == "critico"
    assert resultado[0]["fundamento_legal"] is not None


def test_riesgo_alto_modificacion_unilateral():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": "La empresa se reserva el derecho de modificar unilateralmente el contrato."}])
    assert resultado[0]["riesgo"] in ("alto", "critico")


def test_riesgo_prorroga_automatica():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": "El contrato tiene prórroga automática sin consentimiento del arrendatario."}])
    assert resultado[0]["riesgo"] in ("medio", "alto")


def test_simplificacion_texto():
    detector = RiskDetector()
    simplificado = detector._simplificar("en consecuencia, el arrendatario deberá pagar")
    assert "por lo tanto" in simplificado


def test_simplificacion_no_obstante():
    detector = RiskDetector()
    simplificado = detector._simplificar("no obstante lo anterior, el contrato continúa")
    assert "sin embargo" in simplificado


def test_clausula_abusiva_ingreso_sin_aviso():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": "El arrendador podrá ingresar al inmueble sin previo aviso."}])
    assert resultado[0]["riesgo"] == "critico"


def test_multiples_clausulas():
    detector = RiskDetector()
    clausulas = [
        {"texto": "El plazo del contrato es de 12 meses."},
        {"texto": "El cliente renuncia a cualquier acción legal contra la empresa."},
        {"texto": "Los cargos adicionales no especificados serán cobrados automáticamente."},
    ]
    resultados = detector.analizar(clausulas)
    assert len(resultados) == 3
    assert resultados[0]["riesgo"] == "bajo"
    assert resultados[1]["riesgo"] == "critico"
    assert resultados[2]["riesgo"] == "alto"


def test_texto_vacio_no_crash():
    detector = RiskDetector()
    resultado = detector.analizar([{"texto": ""}])
    assert resultado == []
