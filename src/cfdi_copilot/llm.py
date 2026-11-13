"""Minimal async LLM client over Ollama's HTTP API, built on httpx.

Week 1 goal: one long-lived AsyncClient, explicit timeouts, typed responses.
Retries/backoff and structured outputs arrive on Wednesday.
"""

from __future__ import annotations

import os
import time
from types import TracebackType
from typing import Any, Self

import httpx
from pydantic import BaseModel, Field

DEFAULT_TIMEOUT = httpx.Timeout(connect=2.0, read=60.0, write=10.0, pool=5.0)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResult(BaseModel):
    model: str
    content: str
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    latency_ms: float


class OllamaClient:
    """Use as `async with OllamaClient() as llm:` so the connection pool is closed."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        *,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.model: str = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        url: str = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._http = httpx.AsyncClient(
            base_url=url,
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.0,
        json_schema: dict[str, Any] | None = None,
    ) -> ChatResult:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [m.model_dump() for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        # TODO(B2): si llega json_schema, mándalo a Ollama en payload["format"].
        #   Eso activa structured outputs: Ollama restringe la generación
        #   a JSON que cumple el schema.
        #   Docs: https://ollama.com/blog/structured-outputs
        start = time.perf_counter()
        response = await self._http.post("/api/chat", json=payload)
        response.raise_for_status()
        latency_ms = (time.perf_counter() - start) * 1000
        data = response.json()
        return ChatResult(
            model=data.get("model", self.model),
            content=data["message"]["content"],
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            latency_ms=latency_ms,
        )
