# cfdi-copilot

A RAG + agent copilot for **CFDI 4.0** (Mexican electronic invoices), built in public over 8 weeks.
It answers questions about CFDI 4.0 citing official public SAT documents, and extracts and
validates data from **synthetic** invoices. No real taxpayer data is ever used.

## Roadmap

| Version | Week | What |
|---|---|---|
| v0 | S2 | RAG with citations over pgvector + FastAPI |
| v1 | S3-S4 | Evals in CI + Langfuse tracing (public milestone) |
| v2 | S5-S6 | LangGraph agent with MCP tools + guardrails (OWASP LLM Top 10) |
| v3 | S7-S8 | AWS deploy with CDK (ECS Fargate, RDS pgvector) and measured costs |

Current status: **week 1**. Typed CFDI models (Pydantic v2) and an async LLM client (httpx) are done;
`POST /extract` is a skeleton with failing tests waiting to be implemented.

## Design docs

The system is designed before it is coded. [`docs/diseno/`](docs/diseno/README.md) (in Spanish)
explains what each piece does and how data flows between them, with diagrams: the CFDI domain model,
the architecture, the `/extract` flow step by step, RAG, the agent and MCP, security, the data model,
evals and deployment. Each decision is logged with the alternative it beat and the cost it accepts.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and, optionally, [Ollama](https://ollama.com) running locally.

```bash
uv sync                                  # creates .venv with Python 3.12 + deps
uv run pytest                            # tests (no LLM needed)
uv run python scripts/day01_bench.py     # validation + async benchmark (mocked LLM)
uv run python scripts/day01_bench.py --real --calls 10   # same, against local Ollama
```

Config via env vars (see `.env.example`): `OLLAMA_BASE_URL`, `OLLAMA_MODEL` (default `qwen2.5:7b`).

## Layout

```
src/cfdi_copilot/
  models.py      CFDI 4.0 subset as frozen Pydantic v2 models (RFC, totals, IVA checks)
  synthetic.py   deterministic synthetic invoice generator
  llm.py         async Ollama client (one AsyncClient, explicit timeouts)
  extract.py     LLM extraction use case (skeleton, week 1)
  api.py         FastAPI app factory and POST /extract (skeleton, week 1)
scripts/         daily measurement scripts -> results/*.json
tests/           pytest (+ pytest-asyncio, httpx.MockTransport)
docs/diseno/     system design: flows, entities and decisions (Spanish)
docs/semana-NN/  weekly study notes (Spanish)
```

## Numbers

Measured results get added here as the project grows (latency, cost per question, recall@k,
faithfulness).

## Data policy

Only public SAT documentation and generated invoices. RFCs in this repo are random strings with a
valid format; they do not belong to anyone.
