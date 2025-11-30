import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CorpusLegal:
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        self.documentos: dict[str, str] = {}
        self._cargado = False

    def cargar(self):
        if self._cargado:
            return
        if not self.corpus_dir.exists():
            logger.warning("Directorio de corpus no encontrado: %s", self.corpus_dir)
            return
        for archivo in sorted(self.corpus_dir.glob("*.md")):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    self.documentos[archivo.stem] = f.read()
                logger.info("Corpus cargado: %s (%d caracteres)", archivo.name, len(self.documentos[archivo.stem]))
            except Exception as e:
                logger.error("Error cargando %s: %s", archivo.name, e)
        self._cargado = True

    def buscar(self, consulta: str) -> list[dict]:
        self.cargar()
        resultados = []
        consulta_lower = consulta.lower()
        for nombre, contenido in self.documentos.items():
            if consulta_lower in contenido.lower():
                idx = contenido.lower().find(consulta_lower)
                inicio = max(0, idx - 100)
                fin = min(len(contenido), idx + 300)
                extracto = contenido[inicio:fin]
                resultados.append({
                    "fuente": nombre,
                    "extracto": f"...{extracto}...",
                    "relevancia": 1.0,
                })
        return resultados

    def obtener_todo(self) -> str:
        self.cargar()
        partes = []
        for nombre, contenido in self.documentos.items():
            partes.append(f"## {nombre}\n{contenido}")
        return "\n\n".join(partes)
