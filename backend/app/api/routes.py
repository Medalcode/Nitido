import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schemas import AnalisisRequest, AnalisisResponse, ClausulaResult, ErrorResponse
from app.models.database import get_db, DocumentAnalysis
from app.services.parser import DocumentParser
from app.services.risk_detector import RiskDetector
from app.services.corpus import CorpusLegal
from app.services.summarizer import LegalSummarizer
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
parser = DocumentParser()
risk_detector = RiskDetector()
corpus = CorpusLegal(settings.corpus_dir)
summarizer = LegalSummarizer(settings.gemini_api_key, settings.groq_api_key)


@router.post(
    "/analizar",
    response_model=AnalisisResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Analizar documento legal",
    description="Recibe texto legal y devuelve resumen, cláusulas de riesgo, glosario y recomendaciones.",
)
async def analizar_documento(request: AnalisisRequest, db: AsyncSession = Depends(get_db)):
    contenido = request.contenido.strip()
    if len(contenido) < 10:
        raise HTTPException(400, detail="El documento debe tener al menos 10 caracteres")
    if len(contenido) > settings.max_document_length:
        raise HTTPException(400, detail=f"El documento excede el máximo de {settings.max_document_length} caracteres")

    logger.info("Analizando documento: %d caracteres, tipo=%s", len(contenido), request.tipo_documento)

    try:
        clausulas_raw = parser.extract_clausulas(contenido)
        logger.debug("Cláusulas extraídas: %d", len(clausulas_raw))

        clausulas_analizadas = risk_detector.analizar(clausulas_raw)
        logger.debug("Cláusulas analizadas: %d con riesgo", sum(1 for c in clausulas_analizadas if c.get("riesgo") in ("alto", "critico")))

        # Búsqueda semántica en el Corpus
        resultados_corpus = corpus.buscar(contenido[:1000], n_resultados=3)
        contexto_legal = "\n".join([f"- {r['extracto']}" for r in resultados_corpus])
        logger.debug("Contexto legal encontrado: %d fragmentos", len(resultados_corpus))

        resumen_data = await summarizer.resumir(contenido, contexto_legal)

        clausulas_result = []
        for c in clausulas_analizadas:
            clausulas_result.append(ClausulaResult(
                texto_original=c["texto"],
                texto_simple=c.get("texto_simple", c["texto"]),
                riesgo=c.get("riesgo", "bajo"),
                fundamento_legal=c.get("fundamento_legal"),
                sugerencia=c.get("sugerencia"),
            ))

        response = AnalisisResponse(
            resumen=resumen_data.get("resumen", "No se pudo generar resumen."),
            clausulas=clausulas_result,
            glosario=resumen_data.get("glosario", {}),
            puntaje_riesgo=sum(1 for c in clausulas_analizadas if c.get("riesgo") in ("alto", "critico")),
            total_clausulas=len(clausulas_result),
            recomendaciones=resumen_data.get("recomendaciones", []),
        )

        # Guardar en base de datos
        db_analysis = DocumentAnalysis(
            content_preview=contenido[:500],
            risk_score=response.puntaje_riesgo,
            result_json=response.model_dump()
        )
        db.add(db_analysis)
        await db.commit()

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error inesperado al analizar documento")
        raise HTTPException(500, detail=f"Error interno al procesar el documento: {str(e)}")


@router.post(
    "/analizar/pdf",
    summary="Analizar documento PDF",
    description="Sube un PDF con texto legal y recibe el análisis completo.",
)
async def analizar_pdf(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, detail="Solo se aceptan archivos PDF")

    try:
        contenido = await file.read()
        texto = parser.parse_pdf(contenido)
        if not texto.strip():
            raise HTTPException(422, detail="No se pudo extraer texto del PDF. Asegúrate de que contenga texto seleccionable.")

        logger.info("PDF procesado: %s (%d caracteres)", file.filename, len(texto))
        return await analizar_documento(AnalisisRequest(contenido=texto), db)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error al procesar PDF: %s", file.filename)
        raise HTTPException(500, detail=f"Error al procesar el PDF: {str(e)}")


@router.get("/corpus", summary="Listar documentos del corpus legal")
async def listar_corpus():
    corpus.cargar()
    if not corpus.collection:
        return {"documentos": [], "total": 0}
        
    try:
        data = corpus.collection.get()
        fuentes = list(set([m["fuente"] for m in data.get("metadatas", [])])) if data.get("metadatas") else []
        return {
            "documentos": fuentes,
            "total": len(fuentes),
        }
    except Exception:
        return {"documentos": [], "total": 0}

@router.get("/historial", summary="Obtener historial de análisis")
async def obtener_historial(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(DocumentAnalysis).order_by(DocumentAnalysis.created_at.desc()).limit(10))
        historial = result.scalars().all()
        return [{"id": h.id, "preview": h.content_preview, "risk_score": h.risk_score, "date": h.created_at} for h in historial]
    except Exception as e:
        logger.error("Error al obtener historial: %s", e)
        raise HTTPException(500, detail="Error al acceder a la base de datos")
