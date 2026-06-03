import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class CorpusLegal:
    def __init__(self, corpus_dir: Path):
        self.corpus_dir = corpus_dir
        # Usamos ChromaDB de forma local para persistencia
        db_path = corpus_dir.parent / "chroma_db"
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self._cargado = False
        
        try:
            self.collection = self.client.get_or_create_collection(
                name="leyes_chilenas",
                embedding_function=self.ef
            )
        except Exception as e:
            logger.error("Error al inicializar ChromaDB: %s", e)
            self.collection = None

    def cargar(self):
        if self._cargado or not self.collection:
            return
            
        if self.collection.count() > 0:
            logger.info("Corpus ya cargado en ChromaDB (%d fragmentos)", self.collection.count())
            self._cargado = True
            return

        if not self.corpus_dir.exists():
            logger.warning("Directorio de corpus no encontrado: %s", self.corpus_dir)
            return
            
        logger.info("Iniciando carga del corpus en ChromaDB...")
        for archivo in sorted(self.corpus_dir.glob("*.md")):
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                
                # Dividir el archivo en fragmentos simples (por ejemplo, párrafos grandes o artículos)
                fragmentos = [p.strip() for p in contenido.split("\n\n") if len(p.strip()) > 50]
                
                if not fragmentos:
                    continue
                    
                ids = [f"{archivo.stem}_{i}" for i in range(len(fragmentos))]
                metadatas = [{"fuente": archivo.name} for _ in fragmentos]
                
                self.collection.add(
                    documents=fragmentos,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info("Cargado %s (%d fragmentos)", archivo.name, len(fragmentos))
            except Exception as e:
                logger.error("Error cargando %s en ChromaDB: %s", archivo.name, e)
                
        self._cargado = True

    def buscar(self, consulta: str, n_resultados: int = 3) -> list[dict]:
        self.cargar()
        if not self.collection:
            return []
            
        try:
            resultados = self.collection.query(
                query_texts=[consulta],
                n_results=n_resultados
            )
            
            docs_encontrados = []
            if resultados and "documents" in resultados and resultados["documents"]:
                for i in range(len(resultados["documents"][0])):
                    docs_encontrados.append({
                        "fuente": resultados["metadatas"][0][i]["fuente"],
                        "extracto": resultados["documents"][0][i],
                        "relevancia": resultados["distances"][0][i] if "distances" in resultados and resultados["distances"] else 1.0,
                    })
            return docs_encontrados
        except Exception as e:
            logger.error("Error al buscar en ChromaDB: %s", e)
            return []

    def obtener_todo(self) -> str:
        # Método para retrocompatibilidad, no recomendado para un corpus grande.
        self.cargar()
        if not self.collection:
            return ""
        
        try:
            data = self.collection.get()
            docs = data.get("documents", [])
            return "\n\n".join(docs)
        except Exception as e:
            logger.error("Error al obtener todo de ChromaDB: %s", e)
            return ""
