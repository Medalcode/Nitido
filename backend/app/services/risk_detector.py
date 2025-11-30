class RiskDetector:
    CLAUSULAS_ABUSIVAS = [
        "el arrendador podrá ingresar al inmueble sin previo aviso",
        "no se aceptan devoluciones bajo ninguna circunstancia",
        "el cliente renuncia a cualquier acción legal",
        "la empresa se reserva el derecho de modificar unilateralmente",
        "cargos adicionales no especificados",
        "renuncia a la garantía legal",
        "prórroga automática sin consentimiento",
        "cobro de comisiones no informadas",
        "responsabilidad limitada al monto pagado",
        "cesión de datos personales sin autorización",
    ]

    PATRONES_RIESGO = {
        "renuncia de derechos": r"renuncia|renunciar\s+a|pierde\s+(todo|cualquier)\s+derecho",
        "modificación unilateral": r"modificar\s+unilateralmente|cambiar\s+sin\s+previo\s+aviso",
        "cobro oculto": r"cargos?\s+(?:adicionales?|no\s+especificados?)|comisiones?\s+no\s+informadas?",
        "prórroga automática": r"pr[óo]rroga\s+autom[áa]tica|renovaci[óo]n\s+autom[áa]tica",
        "renuncia garantía legal": r"renuncia\s+(?:a\s+)?(?:la\s+)?garant[íi]a\s+legal",
    }

    def analizar(self, clausulas: list[dict]) -> list[dict]:
        resultados = []
        for clausula in clausulas:
            texto = clausula["texto"].lower()
            nivel = "bajo"
            fundamento = None
            sugerencia = None

            for nombre, patron in self.PATRONES_RIESGO.items():
                if re.search(patron, texto, re.IGNORECASE):
                    nivel = "alto"
                    fundamento = f"Esta cláusula podría contravenir la Ley N° 19.496 sobre Protección de los Derechos de los Consumidores."
                    sugerencia = f"Solicitar la eliminación o modificación de esta cláusula antes de firmar."

            if any(abusiva in texto for abusiva in self.CLAUSULAS_ABUSIVAS):
                nivel = "critico"
                fundamento = fundamento or "Cláusula potencialmente abusiva según criterios del SERNAC."
                sugerencia = sugerencia or "No firmar hasta que esta cláusula sea eliminada del contrato."

            clausula["riesgo"] = nivel
            clausula["fundamento_legal"] = fundamento
            clausula["sugerencia"] = sugerencia
            clausula["texto_simple"] = self._simplificar(texto)
            resultados.append(clausula)

        return resultados

    def _simplificar(self, texto: str) -> str:
        simplificaciones = {
            r"en\s+consecuencia": "por lo tanto",
            r"a\s+saber": "es decir",
            r"toda\s+vez\s+que": "ya que",
            r"con\s+arreglo\s+a": "de acuerdo con",
            r"en\s+el\s+supuesto\s+de\s+que": "si",
            r"no\s+obstante": "sin embargo",
            r"asimismo": "también",
            r"de\s+conformidad\s+con": "según",
            r"en\s+lo\s+sucesivo": "de ahora en adelante",
            r"a\s+los\s+efectos\s+de": "para",
        }
        for patron, reemplazo in simplificaciones.items():
            texto = re.sub(patron, reemplazo, texto, flags=re.IGNORECASE)
        return texto.strip()
