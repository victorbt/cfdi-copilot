# S1 · Lunes · Python moderno: uv, typing, Pydantic v2, async con httpx

Meta del día: que cfdi-copilot ya tenga **modelos tipados de un CFDI 4.0** y un **cliente LLM async**
con timeouts explícitos, y que tengas dos números medidos. Todo con datos sintéticos.

Ritmo: 3 bloques de 45 min (+10 de descanso). B4 solo si hay energía. Lo difícil (B1, B2) en la mañana.

```
           B1 entender                 B2 aplicar                      B3 medir + 5 líneas
  ┌──────────────────────┐   ┌───────────────────────────┐   ┌─────────────────────────────┐
  │ uv · typing          │   │ models.py  (Comprobante)  │   │ scripts/day01_bench.py      │
  │ Pydantic v2          │──▶│ llm.py     (OllamaClient) │──▶│ µs por factura validada     │
  │ async/await + httpx  │   │ tests/     (60 tests)     │   │ secuencial vs gather vs sem │
  └──────────────────────┘   └───────────────────────────┘   └─────────────────────────────┘
```

> El código del día ya está en el repo como referencia. La idea es que **lo leas, lo rompas y lo
> reescribas a tu manera**, no que lo copies. Si algo no te cuadra, cámbialo: es tu proyecto.

---

## B1 · Entender (45 min)

### 1. uv en 10 minutos

uv es el reemplazo de `pip + venv + pyenv + pip-tools + poetry` en un solo binario (Rust). Lo que
importa para entrevista:

| Comando | Qué hace | Equivalente que ya conoces |
|---|---|---|
| `uv init` | crea `pyproject.toml` | `npm init` |
| `uv add httpx` | agrega dep y actualiza `uv.lock` | `npm install httpx` |
| `uv add --dev pytest` | dep de desarrollo (`[dependency-groups]`) | `npm i -D` |
| `uv sync` | crea `.venv` idéntico al lock | `npm ci` |
| `uv run pytest` | corre dentro del venv sin activarlo | `npx` |
| `.python-version` | fija la versión; uv la descarga si no está | `.nvmrc` |

Trade-off: es rapidísimo y reproducible (`uv.lock` va al repo), pero es joven; en algunas empresas
todavía verás poetry o pip-tools. Saber explicar *por qué* un lockfile importa vale más que la herramienta.

Ejercicio: en `/tmp`, `uv init demo && cd demo && uv add httpx && cat uv.lock | head -30`.

### 2. typing moderno (3.12)

- `str | None` en vez de `Optional[str]`; `list[int]` en vez de `List[int]`.
- `Annotated[str, AfterValidator(...)]`: un tipo con reglas pegadas (lo usamos para `Rfc`).
- `Self` para métodos que regresan la misma clase (`__aenter__`).
- `StrEnum` para catálogos del SAT (`TipoDeComprobante = "I" | "E" | ...`).
- Los tipos **no se validan en runtime**; eso lo hace Pydantic. mypy los revisa antes de correr.
  Viniendo de TS: mypy es tu `tsc --noEmit`, Pydantic es la validación en runtime.

### 3. Pydantic v2, lo que sí se pregunta

- `model_validate(dict)` y `model_validate_json(str)` (este último es más rápido: parsea en Rust).
- `Field(alias="Rfc")`: el nombre del XML del SAT ↔ el nombre pythonic.
- `@field_validator` (un campo), `@model_validator(mode="after")` (reglas entre campos, p. ej.
  `Total = SubTotal + IVA`).
- `@computed_field`: valores derivados que salen en el dump (`importe`, `iva`).
- `ConfigDict(frozen=True, extra="forbid")`: inmutable y estricto con campos de más. Clave cuando
  un LLM te regresa JSON: si inventa un campo, truena en vez de pasar en silencio.
- `Decimal` para dinero, nunca `float` (`0.1 + 0.2 != 0.3`).

### 4. async/await + httpx

```
 secuencial:  [req1──────][req2──────][req3──────]          ≈ N × latencia
 gather:      [req1──────]
              [req2──────]                                   ≈ 1 × latencia
              [req3──────]
 gather+sem:  [r1][r2][r3][r4] → [r5][r6]...                 ≈ N/k × latencia, sin tumbar al server
```

- Un `httpx.AsyncClient` **de larga vida** (pool de conexiones), cerrado con `async with`.
  Crear uno por request es un error clásico.
- `httpx.Timeout(connect, read, write, pool)`: por defecto httpx usa 5 s; para un LLM el `read`
  debe ser mayor. Siempre explícito.
- `asyncio.gather` lanza todo a la vez; `asyncio.Semaphore(k)` limita la concurrencia
  (rate limits del proveedor, GPU local de Ollama).
- `asyncio.timeout(s)` (3.11+) pone un límite total a un bloque, además del timeout de httpx.
- Viniendo de Go: `gather` ≈ lanzar goroutines + `WaitGroup`; el semáforo ≈ un canal con buffer k.
  Diferencia: asyncio es un solo hilo cooperativo; si haces CPU pesado dentro, bloqueas todo.

---

## B2 · Aplicarlo a cfdi-copilot (45 min)

Archivos del día:

- `src/cfdi_copilot/models.py`: `Comprobante`, `Emisor`, `Receptor`, `Concepto` con alias del Anexo 20,
  validación de RFC, CP, `Decimal` y la regla `Total = SubTotal + IVA`.
- `src/cfdi_copilot/synthetic.py`: generador determinista (`seed`) de facturas falsas.
- `src/cfdi_copilot/llm.py`: `OllamaClient` async con timeouts y respuesta tipada (tokens + latencia).
- `tests/`: 60 tests; el LLM se simula con `httpx.MockTransport`, así que no necesitas Ollama para correrlos.

Pasos:

1. `cd ~/IAProjects/cfdi-copilot && uv sync && uv run pytest` (todo verde).
2. Rompe algo a propósito: quita `extra="forbid"` y mete un campo inventado. ¿Qué test falla?
3. Agrega tú un campo: `FormaPago` (catálogo `c_FormaPago`: `"01"` efectivo, `"03"` transferencia,
   `"04"` tarjeta de crédito, `"99"` por definir) como `StrEnum`, con su test.
4. `uv run mypy src && uv run ruff check .` en verde antes del commit.

---

## B3 · Medir + 5 líneas (45 min)

```bash
uv run python scripts/day01_bench.py                       # LLM simulado (300 ms por llamada)
uv run python scripts/day01_bench.py --real --calls 10     # contra tu Ollama local
```

Resultado de referencia (simulado, en la máquina donde se armó el repo):

| Métrica | Valor |
|---|---|
| Validar 1 factura con Pydantic v2 | ~19 µs |
| Facturas corruptas detectadas (5 tipos de error) | 100 % |
| 20 llamadas secuenciales | 6.0 s |
| 20 llamadas con `gather` | 0.3 s |
| 20 llamadas con `gather` + `Semaphore(4)` | 1.5 s |

Con `--real` vas a ver otra historia: Ollama en una sola GPU/CPU **no** escala igual con `gather`,
porque el modelo atiende pocas peticiones en paralelo (`OLLAMA_NUM_PARALLEL`). Anota tus números:
esa diferencia entre "concurrencia del cliente" y "capacidad del servidor" es una gran respuesta de entrevista.

> Langfuse entra el jueves; hoy la medición es este script. El jueves estas mismas llamadas ya salen como trazas.

Notas en `docs/notas.md`, 5 líneas:

1. Qué es
2. Cuándo usarlo
3. Trade-off
4. Número medido
5. Pregunta de entrevista que ya puedo contestar

---

## B4 · Si hay energía

- `git commit` del día (mensaje sugerido: `feat: typed CFDI 4.0 models and async LLM client`).
- Revisar el README.
- O usar el bloque para aplicaciones de trabajo.

## Para entrevista

- "¿Por qué `Decimal` y no `float` para montos?"
- "¿Cómo validas JSON que viene de un LLM?" → Pydantic estricto (`extra="forbid"`, validadores de
  negocio), y el miércoles: structured outputs + reintento cuando falla la validación.
- "¿Qué pasa si haces `asyncio.gather` de 1,000 llamadas a un proveedor?" → rate limit / 429;
  semáforo + backoff.
