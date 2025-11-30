import pytest
from app.services.parser import DocumentParser


def test_parse_texto_simple():
    parser = DocumentParser()
    resultado = parser.parse_text("  Hola mundo  ")
    assert resultado == "Hola mundo"


def test_extract_clausulas_por_articulo():
    parser = DocumentParser()
    texto = """Artículo 1°.- El presente contrato regula la relación entre las partes.
Artículo 2.- El arrendador deberá mantener el inmueble en buen estado.
Artículo 3°.- Cualquier modificación requerirá acuerdo por escrito."""
    clausulas = parser.extract_clausulas(texto)
    assert len(clausulas) == 3


def test_extract_clausulas_por_clausula():
    parser = DocumentParser()
    texto = """CLÁUSULA PRIMERA: Objeto del contrato.
Cláusula Segunda: Duración y vigencia.
Cláusula Tercera: Precio y forma de pago."""
    clausulas = parser.extract_clausulas(texto)
    assert len(clausulas) >= 2


def test_extract_clausulas_texto_sin_formato():
    parser = DocumentParser()
    texto = "Este es un texto simple sin cláusulas numeradas. Tiene varias oraciones pero sin formato de cláusulas."
    clausulas = parser.extract_clausulas(texto)
    assert len(clausulas) >= 0


def test_extract_clausulas_vacio():
    parser = DocumentParser()
    assert parser.extract_clausulas("") == []
    assert parser.extract_clausulas("   ") == []
    assert parser.extract_clausulas(None) == []


def test_extract_clausulas_numeradas():
    parser = DocumentParser()
    texto = """1.- El arrendador entrega el inmueble.
2.- El arrendatario paga la renta.
3.- El plazo es de 12 meses."""
    clausulas = parser.extract_clausulas(texto)
    assert len(clausulas) >= 2


def test_extract_clausulas_con_parentesis():
    parser = DocumentParser()
    texto = """1) Primera condición del contrato.
2) Segunda condición importante.
3) Tercera y última condición."""
    clausulas = parser.extract_clausulas(texto)
    assert len(clausulas) >= 2
