from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models.schemas import AnalisisRequest, AnalisisResponse, Clausula
from app.services.parser import DocumentParser
from app.services.risk_detector import RiskDetector
from app.services.corpus import CorpusLegal
from app.services.summarizer import LegalSummarizer
from app.config import settings

router = APIRouter()
parser = DocumentParser()
risk_detector = RiskDetector()
corpus = CorpusLegal(settings.corpus_dir)
summarizer = LegalSummarizer(settings.gemini_api_key)


@router.post("/analizar", response_model=AnalisisResponse)
async def analizar_documento(request: AnalisisRequest):
    contenido = request.contenido
    if not contenido or len(contenido) < 10:
        raise HTTPException(400, "El documento debe tener al menos 10 caracteres")

    clausulas_raw = parser.extract_clausulas(contenido)
    clausulas_analizadas = risk_detector.analizar(clausulas_raw)

    corpus.cargar()
    resumen_data = await summarizer.resumir(contenido)

    glosario = {
        "arrendador": "Dueño de la propiedad que arrienda",
        "arrendatario": "Persona que arrienda",
        "usufructo": "Derecho a usar algo que es de otro",
    }

    return AnalisisResponse(
        resumen=resumen_data["resumen"],
        clausulas=[Clausula(**c) for c in clausulas_analizadas],
        glosario=glosario,
        puntaje_riesgo=sum(1 for c in clausulas_analizadas if c.get("riesgo") in ("alto", "critico")),
        recomendaciones=["Revisar las cláusulas marcadas en rojo antes de firmar"],
    )


@router.post("/analizar/pdf")
async def analizar_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Solo se aceptan archivos PDF")

    contenido = file.file.read()
    texto = parser.parse_pdf(contenido)
    return await analizar_documento(AnalisisRequest(contenido=texto))
