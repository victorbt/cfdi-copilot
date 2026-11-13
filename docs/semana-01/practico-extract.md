# S1 · Sesión práctica · `POST /extract` (FastAPI + structured outputs con Ollama)

Meta: mandas el texto de una factura sintética y regresa un `Comprobante` validado.
Tú escribes el código. Los tests de `tests/test_api.py` ya están escritos y hoy fallan (6 en rojo).
Tu trabajo es ponerlos en verde.

```
 texto factura ──▶ POST /extract ──▶ ExtractRequest (≤20k chars)
                        │
                        ▼
              extract_comprobante()
                        │  system prompt + texto + JSON Schema (format)
                        ▼
                 Ollama /api/chat  ──▶  JSON
                        │
                        ▼
         Comprobante.model_validate_json()
            │ ok                    │ ValidationError
            ▼                       ▼
         200 + CFDI          422 + errores    (LLM caído 502 · timeout 504)
```

```bash
cd ~/IAProjects/cfdi-copilot && uv sync
uv run pytest tests/test_api.py -x      # -x: para en el primer fallo
```

## B1 · FastAPI async (45 min) · `src/cfdi_copilot/api.py`

1. `ExtractRequest.text` con límites.
2. `lifespan`: crea y cierra el `OllamaClient` (uno para toda la app, igual que el lunes).
3. `POST /extract` y el mapeo de errores a 422/502/504.

Conceptos:
- **lifespan** = el "startup/shutdown" de la app. Ahí van los recursos caros (clientes HTTP,
  pools de DB). En Go sería crear el `http.Client` en `main()` e inyectarlo en el handler.
- **App factory** (`create_app(llm)`): así los tests inyectan un LLM falso sin tocar el código.
- **`ASGITransport` no corre el lifespan**: por eso el test lo abre a mano (`client_for`).
- `response_model=Comprobante`: FastAPI valida y serializa la salida, y la documenta en `/docs`.

Al final del B1 tiene que pasar `test_short_text_is_rejected_before_calling_llm`.

## B2 · Structured outputs (45 min) · `extract.py` + `llm.py`

1. `llm.chat(..., json_schema=...)` debe mandar el schema en `payload["format"]`.
2. `comprobante_schema()` con los alias del SAT.
3. `extract_comprobante()`: llamada, `model_validate_json` y `ExtractionError`.

Conceptos:
- **Structured outputs** (Ollama `format`, OpenAI `response_format`): el proveedor restringe la
  generación al schema. Te garantiza **forma** (JSON válido con esas llaves), no **verdad**:
  el LLM puede poner un total que no cuadra. Por eso validas con Pydantic de todos modos.
- Doble defensa: schema en el proveedor y reglas de negocio en tu modelo (`_check_totals`).
- Ollama solo es para desarrollar ($0). No lo uses como juez ni para medir calidad final
  (eso llega en S3 con un modelo mejor).

Al final del B2, los 6 tests en verde, y `uv run mypy src && uv run ruff check .` limpio.

## B3 · Medir (45 min) · `scripts/s1_extract_bench.py`

Con Ollama corriendo (`ollama serve`, modelo `qwen2.5:7b` o el que tengas):

```bash
uv run uvicorn cfdi_copilot.api:app --reload     # prueba a mano en http://localhost:8000/docs
uv run python scripts/s1_extract_bench.py --n 20
```

Completa los TODO de métricas: `valid_pct`, `exact_total_pct`, `top_failing_fields`, p50/p95.
La pregunta clave: **¿puede salir 200 con datos equivocados?** (Pista: tu modelo valida que el
total cuadre con los conceptos, pero no que el RFC sea el del texto.) Ese hueco es la razón de
los evals de la S3.

5 líneas en `docs/notas.md`: qué es, cuándo usarlo, trade-off, número medido, pregunta de entrevista.

## B4 (opcional)

- `git commit -m "feat: /extract endpoint with structured outputs"`.
- O el adelanto del miércoles: si hay `ExtractionError`, reintenta 1 vez mandándole al LLM sus
  propios errores de validación. Mide cuánto sube `valid_pct` y cuánto cuesta en latencia.

## Ya contestas en entrevista

1. ¿Cómo garantizas que la salida del LLM sea JSON válido? → structured outputs + Pydantic estricto
   + 422 explícito (nunca guardas algo que no validó).
2. ¿Qué código HTTP regresas cuando falla el LLM y por qué?
3. ¿Por qué el cliente HTTP vive en el lifespan y no en el endpoint?
