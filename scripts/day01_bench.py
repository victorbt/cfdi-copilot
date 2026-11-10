"""S1 · Monday · B3: measure what you built today.

1. Pydantic v2: how long does validating one synthetic CFDI take, and what
   fraction of corrupted invoices does it catch?
2. async/await + httpx: N calls sequential vs asyncio.gather vs gather with
   a Semaphore (simulated latency by default, real Ollama with --real).

Writes results/day01.json. Run: uv run python scripts/day01_bench.py [--real]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import statistics
import time
from collections.abc import Awaitable, Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from cfdi_copilot.llm import ChatMessage, OllamaClient
from cfdi_copilot.models import Comprobante
from cfdi_copilot.synthetic import fake_comprobante

RESULTS = Path(__file__).resolve().parent.parent / "results" / "day01.json"


def bench_validation(n: int = 5_000) -> dict[str, Any]:
    raws = [fake_comprobante(i) for i in range(n)]
    start = time.perf_counter()
    for raw in raws:
        Comprobante.model_validate(raw)
    us_per_doc = (time.perf_counter() - start) / n * 1e6

    # Corrupt one thing per invoice and count how many the model catches.
    rng = random.Random(42)
    corruptions: list[Callable[[dict[str, Any]], None]] = [
        lambda r: r["Emisor"].__setitem__("Rfc", "XXX"),
        lambda r: r.__setitem__("Total", str(Decimal(r["Total"]) + Decimal("0.5"))),
        lambda r: r["Receptor"].__setitem__("DomicilioFiscalReceptor", "123"),
        lambda r: r.__setitem__("Conceptos", []),
        lambda r: r.__setitem__("Moneda", "EUR"),
    ]
    caught = 0
    for raw in raws[:1_000]:
        rng.choice(corruptions)(raw)
        try:
            Comprobante.model_validate(raw)
        except ValidationError:
            caught += 1
    return {"docs": n, "us_per_doc": round(us_per_doc, 1), "corrupted_caught_pct": caught / 10}


async def bench_async(real: bool, n: int, latency_s: float) -> dict[str, Any]:
    async def handler(request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(latency_s)
        return httpx.Response(200, json={"model": "sim", "message": {"content": "ok"}})

    transport = None if real else httpx.MockTransport(handler)
    prompts = [
        f"En una línea: ¿qué es el campo {f} en un CFDI 4.0?"
        for f in [
            "UsoCFDI",
            "RegimenFiscal",
            "LugarExpedicion",
            "SubTotal",
            "Moneda",
            "TipoDeComprobante",
            "Folio",
            "Serie",
            "ClaveProdServ",
            "Total",
        ]
    ]
    prompts = (prompts * (n // len(prompts) + 1))[:n]

    async with OllamaClient(transport=transport) as llm:

        def call(p: str) -> Awaitable[Any]:
            return llm.chat([ChatMessage(role="user", content=p)])

        async def sequential() -> list[Any]:
            return [await call(p) for p in prompts]

        async def gathered() -> list[Any]:
            return await asyncio.gather(*(call(p) for p in prompts))

        sem = asyncio.Semaphore(4)

        async def bounded(p: str) -> Any:
            async with sem:
                return await call(p)

        async def gathered_bounded() -> list[Any]:
            return await asyncio.gather(*(bounded(p) for p in prompts))

        out: dict[str, Any] = {
            "mode": "real-ollama" if real else f"simulated-{latency_s}s",
            "model": llm.model,
            "calls": n,
        }
        for name, fn in [
            ("sequential", sequential),
            ("gather", gathered),
            ("gather_sem4", gathered_bounded),
        ]:
            start = time.perf_counter()
            results = await fn()
            wall = time.perf_counter() - start
            lat = [r.latency_ms for r in results]
            out[name] = {
                "wall_s": round(wall, 2),
                "p50_ms": round(statistics.median(lat), 1),
                "max_ms": round(max(lat), 1),
            }
        return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true", help="call local Ollama instead of a mock")
    parser.add_argument("--calls", type=int, default=20)
    parser.add_argument("--latency", type=float, default=0.3, help="simulated latency (s)")
    args = parser.parse_args()

    report = {
        "validation": bench_validation(),
        "async": asyncio.run(bench_async(args.real, args.calls, args.latency)),
    }
    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
