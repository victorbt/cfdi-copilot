"""S1 · Monday · B4: tokens, context window and temperature, measured on local Ollama.

Run: uv run python scripts/day01_llm_basics.py   (needs `ollama serve` and OLLAMA_MODEL pulled)
Writes results/day01_llm_basics.json.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from cfdi_copilot.llm import ChatMessage, OllamaClient
from cfdi_copilot.models import Comprobante
from cfdi_copilot.synthetic import fake_comprobante

RESULTS = Path(__file__).resolve().parent.parent / "results" / "day01_llm_basics.json"

SAMPLES = {
    "es": "La factura electrónica debe incluir el régimen fiscal del receptor y su código postal.",
    "en": "The electronic invoice must include the recipient's tax regime and their postal code.",
    "rfc": "XAXX010101000",
    "invoice_json": Comprobante.model_validate(fake_comprobante(1)).model_dump_json(by_alias=True),
}


async def count_tokens(llm: OllamaClient, text: str, baseline: int) -> int:
    # Ollama reports prompt_eval_count = tokens of the whole templated prompt.
    # Subtract the cost of an empty message to approximate the tokens of `text` alone.
    result = await llm.chat([ChatMessage(role="user", content=text)])
    return result.prompt_tokens - baseline


async def distinct_answers(llm: OllamaClient, temperature: float, runs: int = 5) -> int:
    prompt = "Inventa un nombre corto para una app que revisa facturas CFDI. Solo el nombre."
    answers = set()
    for _ in range(runs):
        r = await llm.chat([ChatMessage(role="user", content=prompt)], temperature=temperature)
        answers.add(r.content.strip().lower())
    return len(answers)


async def main() -> None:
    async with OllamaClient() as llm:
        baseline = (await llm.chat([ChatMessage(role="user", content="")])).prompt_tokens
        tokens: dict[str, Any] = {}
        for name, text in SAMPLES.items():
            n = await count_tokens(llm, text, baseline)
            tokens[name] = {
                "chars": len(text),
                "tokens": n,
                "chars_per_token": round(len(text) / max(n, 1), 2),
            }
        report = {
            "model": llm.model,
            "tokens": tokens,
            "distinct_answers_of_5": {
                "T=0": await distinct_answers(llm, 0.0),
                "T=1": await distinct_answers(llm, 1.0),
            },
        }
    RESULTS.parent.mkdir(exist_ok=True)
    RESULTS.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
