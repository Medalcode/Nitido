import re
import logging

logger = logging.getLogger(__name__)


class RiskDetector:
    CLAUSULAS_ABUSIVAS: list[tuple[str, str, str]] = [
        ("ingreso sin aviso", "el arrendador podrá ingresar al inmueble sin previo aviso",
         "Violación del derecho a la inviolabilidad del hogar (Art. 19 N°5 CPR)."),
        ("no devolución", "no se aceptan devoluciones bajo ninguna circunstancia",
         "Contraviene la garantía legal de productos (Ley 19.496 Art. 20)."),
        ("renuncia acciones legales", "renuncia a cualquier acción legal",
         "Renuncia anticipada de derechos es nula (Ley 19.496 Art. 16)."),
        ("modificación unilateral", "se reserva el derecho de modificar unilateralmente",
         "Modificación unilateral del contrato es abusiva (Ley 19.496 Art. 16 letra a)."),
        ("cargos ocultos", "cargos adicionales no especificados",
         "Omisión de información relevante (Ley 19.496 Art. 3)."),
        ("renuncia garantía", "renuncia a la garantía legal",
         "Renuncia a garantía legal es nula (Ley 19.496 Art. 16)."),
        ("prórroga automática", "prórroga automática sin consentimiento",
         "Prórroga automática sin derecho a término anticipado es abusiva (Ley 19.496 Art. 16)."),
        ("comisiones no informadas", "cobro de comisiones no informadas",
         "Omisión de información esencial (Ley 19.496 Art. 3)."),
        ("responsabilidad limitada", "responsabilidad limitada al monto pagado",
         "Limitación de responsabilidad es abusiva (Ley 19.496 Art. 16 letra d)."),
        ("cesión datos", "cesión de datos personales sin autorización",
         "Violación a la Ley 19.628 sobre protección de datos personales."),
    ]

    PATRONES_RIESGO: dict[str, tuple[str, str, str]] = {
        "renuncia de derechos": (
            r"renuncia(?:r)?\s+(?:a\s+|de\s+)?(?:todo|todos|cualquier|sus|los)\s+derecho",
            "Alto",
            "Renuncia anticipada de derechos del consumidor es nula (Ley 19.496 Art. 16 letra b).",
        ),
        "modificación unilateral": (
            r"modificar\s+unilateralmente|(?:reservarse|cambiar)\s+sin\s+(?:previo\s+)?(?:aviso|consentimiento)",
            "Alto",
            "La modificación unilateral del contrato es abusiva (Ley 19.496 Art. 16 letra a).",
        ),
        "cobro no informado": (
            r"cargos?\s+(?:adicionales?|no\s+especificados?|extraordinarios)|comisiones?\s+no\s+informadas?",
            "Alto",
            "Cobros no informados vulneran el derecho a información veraz (Ley 19.496 Art. 3).",
        ),
        "prórroga automática": (
            r"pr[óo]rroga\s+autom[áa]tica|renovaci[óo]n\s+autom[áa]tica",
            "Medio",
            "Prórroga automática sin derecho a término anticipado puede ser abusiva.",
        ),
        "renuncia garantía legal": (
            r"renuncia\s+(?:a\s+)?(?:la\s+)?garant[íi]a\s+legal",
            "Crítico",
            "La renuncia a la garantía legal es nula absolutamente (Ley 19.496 Art. 16).",
        ),
        "inversión carga prueba": (
            r"invierte\s+la\s+carga\s+de\s+la\s+prueba|el\s+consumidor\s+deber[áa]\s+probar",
            "Crítico",
            "Inversión de la carga de la prueba en perjuicio del consumidor es nula (Ley 19.496 Art. 16 letra c).",
        ),
        "tribunales distintos": (
            r"someterse?\s+a\s+(?:los\s+)?tribunales?\s+de\s+(?!su\s+domicilio)",
            "Alto",
            "Obligar al consumidor a tribunales distintos de su domicilio es abusivo (Ley 19.496 Art. 16 letra g).",
        ),
    }

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

        for nombre, (patron, nivel_detectado, fund) in self.PATRONES_RIESGO.items():
            if re.search(patron, texto, re.IGNORECASE):
                riesgo_num = {"bajo": 0, "medio": 1, "alto": 2, "critico": 3}
                if riesgo_num.get(nivel_detectado.lower(), 0) > riesgo_num.get(nivel, 0):
                    nivel = nivel_detectado.lower()
                    fundamento = fund
                    sugerencia = self._sugerencia_para(nombre)

        for nombre_abusivo, patron_abusivo, fund_abusivo in self.CLAUSULAS_ABUSIVAS:
            if patron_abusivo.lower() in texto:
                if nivel != "critico":
                    nivel = "critico"
                    fundamento = fund_abusivo
                    sugerencia = "No firmar hasta que esta cláusula sea eliminada del contrato."
                break

        return nivel, fundamento, sugerencia

    def _sugerencia_para(self, nombre: str) -> str:
        sugerencias = {
            "renuncia de derechos": "Solicitar la eliminación de esta cláusula. Es nula por ley.",
            "modificación unilateral": "Exigir que cualquier modificación requiera aprobación por escrito.",
            "cobro no informado": "Solicitar detalle completo de todos los costos antes de firmar.",
            "prórroga automática": "Pedir que la renovación requiera confirmación expresa.",
            "renuncia garantía legal": "Esta cláusula es nula. La garantía legal es irrenunciable.",
            "inversión carga prueba": "Esta cláusula es nula. El proveedor debe probar.",
            "tribunales distintos": "Solicitar que las disputas se resuelvan en el domicilio del consumidor.",
        }
        return sugerencias.get(nombre, "Revisar esta cláusula con atención antes de firmar.")

    def _simplificar(self, texto: str) -> str:
        simplificaciones = {
            r"\ben\s+consecuencia\b": "por lo tanto",
            r"\ba\s+saber\b": "es decir",
            r"\btoda\s+vez\s+que\b": "ya que",
            r"\bcon\s+arreglo\s+a\b": "de acuerdo con",
            r"\ben\s+el\s+supuesto\s+(?:de\s+)?que\b": "si",
            r"\bno\s+obstante\b": "sin embargo",
            r"\basimismo\b": "también",
            r"\bde\s+conformidad\s+con\b": "según",
            r"\ben\s+lo\s+sucesivo\b": "de ahora en adelante",
            r"\ba\s+los\s+efectos\s+de\b": "para",
            r"\bdicho\s+(?:contrato|documento|acuerdo)\b": "este documento",
            r"\bel\s+(?:suscrito|compareciente|contratante)\b": "la persona",
            r"\bla\s+(?:suscrita|compareciente|contratante)\b": "la persona",
            r"\bprevio\s+pago\b": "antes de pagar",
            r"\bposterior\s+pago\b": "después de pagar",
            r"\ben\s+forma\s+inmediata\b": "de inmediato",
            r"\ba\s+la\s+fecha\s+de\s+cierre\b": "al final",
            r"\bcon\s+posterioridad\b": "después",
            r"\bcon\s+anterioridad\b": "antes",
        }
        for patron, reemplazo in simplificaciones.items():
            texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)
        return texto.strip()
