"""Invoice text -> validated Comprobante, using an LLM with structured outputs.

S1 · práctico · B2. Completa los TODO hasta que pase `uv run pytest tests/test_api.py`.
"""

from __future__ import annotations

from typing import Any

from cfdi_copilot.llm import ChatResult, OllamaClient
from cfdi_copilot.models import Comprobante

# Borrador de prompt. Ajústalo cuando midas en el B3: ¿qué campo falla más y por qué?
SYSTEM_PROMPT = """Eres un extractor de datos de facturas CFDI 4.0.
Devuelve SOLO un objeto JSON que cumpla el JSON Schema dado,
con los nombres de atributo del Anexo 20 (Rfc, Nombre, RegimenFiscal, UsoCFDI, SubTotal, Total...).
Copia los valores tal cual aparecen en el texto. No calcules ni inventes datos.
Los importes van como strings con punto decimal, sin signo de pesos ni comas."""


class ExtractionError(Exception):
    """The LLM answered, but its output is not a valid Comprobante."""

    def __init__(self, message: str, errors: list[dict[str, Any]], raw_output: str) -> None:
        super().__init__(message)
        self.errors = errors
        self.raw_output = raw_output


def comprobante_schema() -> dict[str, Any]:
    """JSON Schema de Comprobante con los alias del SAT (Rfc, Total...), no los nombres Python."""
    # TODO(B2): una línea. Pista: Comprobante.model_json_schema(...) y el parámetro by_alias.
    raise NotImplementedError


async def extract_comprobante(llm: OllamaClient, text: str) -> tuple[Comprobante, ChatResult]:
    """Pide al LLM el JSON del comprobante y valídalo con Pydantic.

    Regresa (comprobante, ChatResult) para que el B3 pueda medir tokens y latencia.
    Si el JSON no es válido (o ni siquiera es JSON), lanza ExtractionError.
    """
    # TODO(B2):
    # 1. Arma dos ChatMessage: system=SYSTEM_PROMPT, user=text.
    # 2. await llm.chat(..., json_schema=comprobante_schema())   (temperature ya es 0 por defecto)
    # 3. Comprobante.model_validate_json(result.content)  -> ojo: _json, no model_validate(dict)
    # 4. Si truena con ValidationError: lanza ExtractionError con
    #    exc.errors(include_url=False, include_context=False, include_input=False)
    #    (sin input/context para que el error sea serializable y no regrese datos de la factura)
    #    y usa `raise ... from exc` para no perder la causa.
    # Pregunta para tus 5 líneas: si el LLM regresa "no sé", ¿qué excepción lanza Pydantic?
    raise NotImplementedError
