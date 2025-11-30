import pytest
from app.services.corpus import CorpusLegal
from pathlib import Path


def test_corpus_carga_archivos(tmp_path):
    (tmp_path / "test-ley.md").write_text("# Ley de prueba\nContenido de prueba.", encoding="utf-8")
    corpus = CorpusLegal(tmp_path)
    corpus.cargar()
    assert "test-ley" in corpus.documentos


def test_corpus_buscar_encuentra_resultados(tmp_path):
    (tmp_path / "test-ley.md").write_text("# Ley de prueba\nCláusula abusiva detectada.", encoding="utf-8")
    corpus = CorpusLegal(tmp_path)
    resultados = corpus.buscar("abusiva")
    assert len(resultados) > 0
    assert resultados[0]["fuente"] == "test-ley"


def test_corpus_buscar_sin_resultados(tmp_path):
    (tmp_path / "test-ley.md").write_text("# Ley de prueba\nContenido normal.", encoding="utf-8")
    corpus = CorpusLegal(tmp_path)
    resultados = corpus.buscar("inexistente")
    assert len(resultados) == 0


def test_corpus_obtener_todo(tmp_path):
    (tmp_path / "ley1.md").write_text("Contenido 1", encoding="utf-8")
    (tmp_path / "ley2.md").write_text("Contenido 2", encoding="utf-8")
    corpus = CorpusLegal(tmp_path)
    todo = corpus.obtener_todo()
    assert "Contenido 1" in todo
    assert "Contenido 2" in todo


def test_corpus_no_crash_sin_directorio():
    corpus = CorpusLegal(Path("/ruta/inexistente"))
    corpus.cargar()
    assert corpus.documentos == {}
