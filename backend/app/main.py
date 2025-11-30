from fastapi import FastAPI
from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="Nitido API",
    description="Descifra documentos legales al español simple",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
