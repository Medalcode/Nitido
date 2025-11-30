import re
import logging
from io import BytesIO

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

logger = logging.getLogger(__name__)


class DocumentParser:
    def parse_pdf(self, content: bytes) -> str:
        if PdfReader is None:
            raise ImportError("PyPDF2 no está instalado. Instálalo con: pip install PyPDF2")
        reader = PdfReader(BytesIO(content))
        texto = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                texto.append(page_text)
            logger.debug("Página %d extraída: %d caracteres", i + 1, len(page_text))
        return "\n".join(texto)

    def parse_text(self, content: str) -> str:
        return content.strip()

    def extract_clausulas(self, text: str) -> list[dict]:
        if not text or not text.strip():
            return []

        clausulas = []
        patron = (
            r"(?:^|\n)\s*"
            r"(?:"
            r"§\s*|"
            r"Art[íi]culo\s+\d+[ªº]?\s*[.—-]?\s*|"
            r"Cl[aá]usula\s+\d+[ªº]?\s*[.—-]?\s*|"
            r"(?:PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[Ée]ptima|OCTAVA|NOVENA|D[Ée]CIMA)"
            r"(?:\s+|$)|"
            r"\d+[.-]\s+|"
            r"\d+\)\s+"
            r")"
            r"([^\n]+(?:\n(?!\s*(?:§|Art[íi]culo|Cl[aá]usula|"
            r"PRIMERA|SEGUNDA|TERCERA|CUARTA|QUINTA|SEXTA|S[Ée]ptima|OCTAVA|NOVENA|D[Ée]CIMA|"
            r"\d+[.-]|\d+\)))[^\n]*)*)"
        )
        matches = re.finditer(patron, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            texto_clausula = match.group(1).strip()
            if texto_clausula and len(texto_clausula) > 10:
                clausulas.append({"texto": texto_clausula, "indice": match.start()})

        if not clausulas:
            parrafos = [p.strip() for p in text.split("\n") if p.strip()]
            clausulas = [{"texto": p, "indice": 0} for p in parrafos if len(p) > 20]

        return clausulas
