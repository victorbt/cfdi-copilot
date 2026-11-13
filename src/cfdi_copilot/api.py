"""FastAPI app. Run: uv run uvicorn cfdi_copilot.api:app --reload  (docs en /docs)

S1 · práctico · B1. Completa los TODO hasta que pase `uv run pytest tests/test_api.py`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from cfdi_copilot.llm import OllamaClient


class ExtractRequest(BaseModel):
    # TODO(B1): un campo `text: str` con min_length=20 y max_length=20_000 (Field).
    #   ¿Por qué un máximo? Piensa en tokens, ventana de contexto y costo (B4 del lunes).
    pass


def create_app(llm: OllamaClient | None = None) -> FastAPI:
    """App factory: los tests pasan un OllamaClient falso; en producción se crea uno real."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # TODO(B1): al arrancar, guarda en app.state.llm el `llm` recibido o crea OllamaClient().
        #   Al apagar (después del yield, en un finally), ciérralo con aclose()
        #   SOLO si lo creaste tú.
        #   ¿Por qué aquí y no dentro del endpoint? (Pista: pool de conexiones, lunes B1.)
        yield

    app = FastAPI(title="cfdi-copilot", lifespan=lifespan)

    # TODO(B1): POST /extract con response_model=Comprobante.
    #   - Recibe `body: ExtractRequest` y `request: Request` (para leer request.app.state.llm).
    #   - Llama a extract_comprobante(...) del módulo extract (B2).
    #   - Mapea errores a HTTP:
    #       ExtractionError         -> 422, detail={"message": str(exc), "errors": exc.errors}
    #       httpx.TimeoutException  -> 504
    #       httpx.HTTPError         -> 502   (ojo con el orden: Timeout es subclase de HTTPError)
    #   Pregunta de entrevista: ¿por qué 422/502/504 y no 500 para todo?

    return app


app = create_app()
