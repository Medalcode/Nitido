import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CorpusLegal:
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.documentos: dict[str, str] = {}

    def cargar(self):
        if not self.corpus_dir.exists():
            logger.warning("Directorio de corpus no encontrado: %s", self.corpus_dir)
            return

        for archivo in self.corpus_dir.glob("*.md"):
            with open(archivo, "r", encoding="utf-8") as f:
                self.documentos[archivo.stem] = f.read()
            logger.info("Cargado: %s", archivo.name)

    def buscar(self, consulta: str) -> list[dict]:
        resultados = []
        consulta_lower = consulta.lower()
        for nombre, contenido in self.documentos.items():
            if consulta_lower in contenido.lower():
                resultados.append({
                    "fuente": nombre,
                    "extracto": contenido[:500],
                })
        return resultados
