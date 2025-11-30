from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class ClausulaResult(BaseModel):
    texto_original: str
    texto_simple: str
    riesgo: RiskLevel
    fundamento_legal: str | None = None
    sugerencia: str | None = None


class AnalisisRequest(BaseModel):
    contenido: str = Field(..., min_length=10, description="Texto del documento legal a analizar")
    tipo_documento: str | None = Field(None, description="contrato, tyc, bancario, isapre, otro")
    contexto: str | None = None


class AnalisisResponse(BaseModel):
    resumen: str
    clausulas: list[ClausulaResult]
    glosario: dict[str, str]
    puntaje_riesgo: int
    total_clausulas: int
    recomendaciones: list[str]
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    error: str
    detalle: str | None = None
