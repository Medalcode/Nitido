import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RiskDetector:
    def __init__(self):
        self.clausulas_abusivas = []
        self.patrones_riesgo = []
        self.simplificaciones = {}
        self.cargar_reglas()

    def cargar_reglas(self):
        ruta_reglas = Path(__file__).parent.parent / "reglas.json"
        try:
            with open(ruta_reglas, "r", encoding="utf-8") as f:
                datos = json.load(f)
                self.clausulas_abusivas = datos.get("clausulas_abusivas", [])
                self.patrones_riesgo = datos.get("patrones_riesgo", [])
                self.simplificaciones = datos.get("simplificaciones", {})
            logger.info("Reglas de riesgo cargadas exitosamente.")
        except Exception as e:
            logger.error("Error cargando reglas.json: %s", e)

    def analizar(self, clausulas: list[dict]) -> list[dict]:
        resultados = []
        for i, clausula in enumerate(clausulas):
            texto = clausula.get("texto", "").lower()
            if not texto:
                continue

            riesgo, fundamento, sugerencia = self._evaluar(texto)

            clausula["riesgo"] = riesgo
            clausula["fundamento_legal"] = fundamento
            clausula["sugerencia"] = sugerencia
            clausula["texto_simple"] = self._simplificar(texto)
            clausula["indice"] = i
            resultados.append(clausula)

        return resultados

    def _evaluar(self, texto: str) -> tuple[str, str | None, str | None]:
        nivel: str = "bajo"
        fundamento: str | None = None
        sugerencia: str | None = None

        for patron_info in self.patrones_riesgo:
            nombre = patron_info["nombre"]
            patron = patron_info["patron"]
            nivel_detectado = patron_info["riesgo"]
            fund = patron_info["fundamento"]
            sug = patron_info.get("sugerencia", "Revisar esta cláusula con atención antes de firmar.")

            if re.search(patron, texto, re.IGNORECASE):
                riesgo_num = {"bajo": 0, "medio": 1, "alto": 2, "critico": 3}
                if riesgo_num.get(nivel_detectado.lower(), 0) > riesgo_num.get(nivel, 0):
                    nivel = nivel_detectado.lower()
                    fundamento = fund
                    sugerencia = sug

        for abusiva_info in self.clausulas_abusivas:
            patron_abusivo = abusiva_info["patron"]
            fund_abusivo = abusiva_info["fundamento"]
            
            if patron_abusivo.lower() in texto:
                if nivel != "critico":
                    nivel = "critico"
                    fundamento = fund_abusivo
                    sugerencia = "No firmar hasta que esta cláusula sea eliminada del contrato."
                break

        return nivel, fundamento, sugerencia

    def _simplificar(self, texto: str) -> str:
        for patron, reemplazo in self.simplificaciones.items():
            texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)
        return texto.strip()
