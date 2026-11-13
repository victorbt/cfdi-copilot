"""S1 · práctico · B3: mide /extract contra tu Ollama local con facturas sintéticas.

Run: uv run python scripts/s1_extract_bench.py --n 20     (necesita `ollama serve`)
Writes results/s1_extract.json.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

from cfdi_copilot.api import create_app
from cfdi_copilot.synthetic import fake_comprobante, render_text

RESULTS = Path(__file__).resolve().parent.parent / "results" / "s1_extract.json"


async def main(n: int) -> None:
    app = create_app()
    rows: list[dict[str, Any]] = []
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        timeout = httpx.Timeout(120.0)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://bench", timeout=timeout
        ) as c:
            for seed in range(1000, 1000 + n):  # semillas distintas a las de los tests
                raw = fake_comprobante(seed)
                start = time.perf_counter()
                resp = await c.post("/extract", json={"text": render_text(raw)})
                rows.append(
                    {
                        "seed": seed,
                        "status": resp.status_code,
                        "ms": (time.perf_counter() - start) * 1000,
                        "body": resp.json(),
                        "expected_total": raw["Total"],
                    }
                )
                print(seed, resp.status_code, round(rows[-1]["ms"]))

    # TODO(B3): calcula y guarda en `report`:
    #   - valid_pct: % de respuestas 200
    #   - exact_total_pct: de las 200, % cuyo body["Total"] == expected_total (como Decimal).
    #     ¿Puede salir 200 con el total mal? Piensa qué valida tu modelo y qué no.
    #   - top_failing_fields: Counter de los "loc" en body["detail"]["errors"] de las 422
    #   - p50_ms y p95_ms (statistics.quantiles(..., n=20)[18] para p95)
    report: dict[str, Any] = {"n": n}
    _ = (statistics, Counter)  # quítalo cuando los uses

    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps({"report": report, "rows": rows}, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    asyncio.run(main(parser.parse_args().n))
