import asyncio
import json

import httpx
import pytest

from cfdi_copilot.llm import ChatMessage, OllamaClient


def fake_ollama(request: httpx.Request) -> httpx.Response:
    body = json.loads(request.content)
    return httpx.Response(
        200,
        json={
            "model": body["model"],
            "message": {"role": "assistant", "content": "hola"},
            "prompt_eval_count": 12,
            "eval_count": 3,
        },
    )


async def test_chat_parses_response() -> None:
    async with OllamaClient(model="fake", transport=httpx.MockTransport(fake_ollama)) as llm:
        result = await llm.chat([ChatMessage(role="user", content="hola")])
    assert result.content == "hola"
    assert result.prompt_tokens == 12
    assert result.completion_tokens == 3


async def test_http_error_is_raised() -> None:
    transport = httpx.MockTransport(lambda r: httpx.Response(500, json={"error": "boom"}))
    async with OllamaClient(model="fake", transport=transport) as llm:
        with pytest.raises(httpx.HTTPStatusError):
            await llm.chat([ChatMessage(role="user", content="hola")])


async def test_timeout_is_raised() -> None:
    async def slow(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(1)
        return fake_ollama(request)

    transport = httpx.MockTransport(slow)
    async with OllamaClient(model="fake", timeout=httpx.Timeout(0.05), transport=transport) as llm:
        with pytest.raises((httpx.TimeoutException, TimeoutError)):
            async with asyncio.timeout(0.1):
                await llm.chat([ChatMessage(role="user", content="hola")])
