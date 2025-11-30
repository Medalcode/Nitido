import re
from PyPDF2 import PdfReader
from io import BytesIO


class DocumentParser:
    def parse_pdf(self, content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)

    def parse_text(self, content: str) -> str:
        return content.strip()

    def extract_clausulas(self, text: str) -> list[dict]:
        clausulas = []
        patterns = [
            r"(?:^|\n)\s*(?:§\s*|Artículo\s+\d+[ªº]?\s*[.—-]?\s*|Cláusula\s+\d+[ªº]?\s*[.—-]?\s*|\d+\.-\s*|\d+\)\s*)([^\n]+(?:\n(?!\s*(?:§|Artículo|Cláusula|\d+\.-|\d+\)))[^\n]*)*)",
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                clausulas.append({"texto": match.group(1).strip(), "indice": match.start()})
        return clausulas or [{"texto": text, "indice": 0}]
