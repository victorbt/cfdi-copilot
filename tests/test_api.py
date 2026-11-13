"""Tests for POST /extract. The LLM is faked with httpx.MockTransport (no Ollama needed).

Note: httpx.ASGITransport does NOT run FastAPI's lifespan, so `client_for` enters it by hand.
"""

import json
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any

import httpx
from fastapi import FastAPI

from cfdi_copilot.api import create_app
from cfdi_copilot.llm import OllamaClient
from cfdi_copilot.synthetic import fake_comprobante, render_text

Handler = Callable[[httpx.Request], httpx.Response]


def llm_answering(content: str, seen: list[dict[str, Any]]) -> Handler:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(
            200, json={"model": "fake", "message": {"role": "assistant", "content": content}}
        )

    return handler


def make_app(handler: Handler) -> FastAPI:
    return create_app(OllamaClient(model="fake", transport=httpx.MockTransport(handler)))


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


async def test_extract_returns_validated_invoice() -> None:
    raw = fake_comprobante(10)
    seen: list[dict[str, Any]] = []
    async with client_for(make_app(llm_answering(json.dumps(raw), seen))) as client:
        resp = await client.post("/extract", json={"text": render_text(raw)})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["Emisor"]["Rfc"] == raw["Emisor"]["Rfc"]
    assert Decimal(body["Total"]) == Decimal(raw["Total"])


async def test_extract_sends_schema_and_text_to_llm() -> None:
    raw = fake_comprobante(11)
    seen: list[dict[str, Any]] = []
    async with client_for(make_app(llm_answering(json.dumps(raw), seen))) as client:
        await client.post("/extract", json={"text": render_text(raw)})
    assert len(seen) == 1
    payload = seen[0]
    assert payload["format"]["title"] == "Comprobante"  # structured outputs
    assert "Rfc" in json.dumps(payload["format"])  # schema uses SAT aliases
    assert payload["options"]["temperature"] == 0
    assert raw["Emisor"]["Rfc"] in payload["messages"][-1]["content"]


async def test_wrong_total_from_llm_is_422() -> None:
    raw = fake_comprobante(12)
    raw["Total"] = str(Decimal(raw["Total"]) + 1)
    async with client_for(make_app(llm_answering(json.dumps(raw), []))) as client:
        resp = await client.post("/extract", json={"text": render_text(raw)})
    assert resp.status_code == 422
    assert "Total" in json.dumps(resp.json()["detail"])


async def test_non_json_from_llm_is_422() -> None:
    raw = fake_comprobante(13)
    async with client_for(make_app(llm_answering("no sé, perdón", []))) as client:
        resp = await client.post("/extract", json={"text": render_text(raw)})
    assert resp.status_code == 422


async def test_short_text_is_rejected_before_calling_llm() -> None:
    seen: list[dict[str, Any]] = []
    async with client_for(make_app(llm_answering("{}", seen))) as client:
        resp = await client.post("/extract", json={"text": "hola"})
    assert resp.status_code == 422
    assert seen == []


async def test_llm_down_is_502() -> None:
    def broken(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    raw = fake_comprobante(14)
    async with client_for(make_app(broken)) as client:
        resp = await client.post("/extract", json={"text": render_text(raw)})
    assert resp.status_code == 502
