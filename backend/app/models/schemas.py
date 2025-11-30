from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"


class Clausula(BaseModel):
    texto_original: str
    texto_simple: str
    riesgo: RiskLevel
    fundamento_legal: str | None = None
    sugerencia: str | None = None


class AnalisisRequest(BaseModel):
    contenido: str
    tipo_documento: str | None = None
    contexto: str | None = None


class AnalisisResponse(BaseModel):
    resumen: str
    clausulas: list[Clausula]
    glosario: dict[str, str]
    puntaje_riesgo: int
    recomendaciones: list[str]
    timestamp: datetime = Field(default_factory=datetime.now)
