# Glosario

> **Estado:** vivo · **Lectura:** de consulta · [Índice](README.md) · Anterior: [10 · Decisiones](10-decisiones.md)

Una línea por término, agrupados por tema. La última columna dice en qué documento se explica con
calma.

## CFDI y dominio fiscal

| Término | Qué es | Más en |
|---|---|---|
| **SAT** | Servicio de Administración Tributaria: la autoridad fiscal mexicana | [02](02-dominio-cfdi.md) |
| **CFDI** | Comprobante Fiscal Digital por Internet: la factura electrónica mexicana, un XML con estructura fija | [02](02-dominio-cfdi.md) |
| **Anexo 20** | El documento del SAT que define la estructura del XML y sus validaciones | [02](02-dominio-cfdi.md) |
| **Emisor / Receptor** | Quien factura y a quien se le factura | [02](02-dominio-cfdi.md) |
| **RFC** | Registro Federal de Contribuyentes: la clave que identifica a cada contribuyente, de 12 caracteres para personas morales y 13 para personas físicas | [02](02-dominio-cfdi.md) |
| **PAC** | Proveedor Autorizado de Certificación: empresa autorizada por el SAT para validar y timbrar | [02](02-dominio-cfdi.md) |
| **CSD** | Certificado de Sello Digital: la llave con la que el emisor firma su XML | [02](02-dominio-cfdi.md) |
| **Timbre / UUID** | La certificación que agrega el PAC; el UUID o folio fiscal identifica al comprobante | [02](02-dominio-cfdi.md) |
| **Concepto** | Cada renglón de la factura: qué se vendió, cantidad, valor unitario e importe | [02](02-dominio-cfdi.md) |
| **Catálogo** | Lista oficial de valores válidos para un campo, por ejemplo `c_UsoCFDI` | [02](02-dominio-cfdi.md) |
| **Uso de CFDI** | Clave que dice para qué usará el receptor la factura, por ejemplo `G03` | [02](02-dominio-cfdi.md) |
| **Régimen fiscal** | Clave del régimen bajo el que tributa un contribuyente, por ejemplo `601` | [02](02-dominio-cfdi.md) |

## LLM

| Término | Qué es | Más en |
|---|---|---|
| **LLM** | Modelo de lenguaje grande: recibe texto y predice el texto que sigue | [03](03-arquitectura.md) |
| **Token** | La unidad en que el modelo parte el texto; se cobra y se limita por tokens | [semana 1](../semana-01/lunes.md) |
| **Ventana de contexto** | El máximo de tokens que caben en una llamada, contando el prompt y la respuesta | [semana 1](../semana-01/lunes.md) |
| **Temperatura** | Qué tanta variación se permite en la salida; con 0 la respuesta es casi repetible | [semana 1](../semana-01/lunes.md) |
| **Prompt de sistema** | Las instrucciones fijas que acompañan a cada llamada | [04](04-flujo-extract.md) |
| **JSON Schema** | Descripción formal de la forma de un JSON: campos, tipos y cuáles son obligatorios | [04](04-flujo-extract.md) |
| **Structured outputs** | Obligar al modelo a responder con un JSON que cumple un schema | [04](04-flujo-extract.md) |
| **Alucinación** | Una respuesta bien redactada que no se apoya en ninguna fuente | [05](05-flujos-rag.md) |

## RAG

| Término | Qué es | Más en |
|---|---|---|
| **RAG** | Generación aumentada por recuperación: buscar primero y redactar con lo encontrado | [05](05-flujos-rag.md) |
| **Ingesta** | El proceso que baja, parte, vectoriza y guarda los documentos | [05](05-flujos-rag.md) |
| **Chunk** | Un fragmento de documento, del tamaño adecuado para buscarlo y citarlo | [05](05-flujos-rag.md) |
| **Embedding** | Un vector de números que representa el significado de un texto | [05](05-flujos-rag.md) |
| **Búsqueda vectorial** | Encontrar los chunks cuyo embedding se parece más al de la pregunta | [05](05-flujos-rag.md) |
| **Búsqueda de texto** | Encontrar los chunks que contienen las palabras de la pregunta | [05](05-flujos-rag.md) |
| **Búsqueda híbrida** | Usar las dos búsquedas y fusionar sus resultados | [05](05-flujos-rag.md) |
| **RRF** | *Reciprocal Rank Fusion*: fusiona dos listas sumando `1 / (k + posición)` | [05](05-flujos-rag.md) |
| **HNSW** | El índice aproximado que hace rápida la búsqueda vectorial | [05](05-flujos-rag.md) |
| **Reranker** | Un modelo que reordena los candidatos leyendo pregunta y chunk juntos | [05](05-flujos-rag.md) |
| **Cita** | La referencia al documento y la página que respaldan una afirmación | [05](05-flujos-rag.md) |
| **Abstención** | Responder "no lo sé" cuando la evidencia no alcanza | [05](05-flujos-rag.md) |

## Evals y observabilidad

| Término | Qué es | Más en |
|---|---|---|
| **Eval** | Un test cuyo resultado es un número que se compara contra un umbral | [08](08-evals-y-observabilidad.md) |
| **Golden set** | Preguntas con respuesta y fuente conocidas, verificadas a mano | [08](08-evals-y-observabilidad.md) |
| **recall@k** | Fracción de las fuentes esperadas que aparecen entre los k recuperados | [08](08-evals-y-observabilidad.md) |
| **MRR** | Promedio de `1 / posición` de la primera fuente correcta | [08](08-evals-y-observabilidad.md) |
| **Faithfulness** | Fracción de las afirmaciones de la respuesta que el contexto respalda | [08](08-evals-y-observabilidad.md) |
| **Juez LLM** | Un modelo que califica respuestas con una rúbrica | [08](08-evals-y-observabilidad.md) |
| **Calibración** | Comparar al juez con etiquetas humanas antes de confiar en él | [08](08-evals-y-observabilidad.md) |
| **Línea base** | La medición inicial contra la que se compara cada cambio | [08](08-evals-y-observabilidad.md) |
| **Traza** | El registro de todo lo que pasó para atender una petición | [08](08-evals-y-observabilidad.md) |
| **Span** | Un paso con inicio y fin dentro de una traza | [08](08-evals-y-observabilidad.md) |
| **Generación** | Un span que es una llamada a un modelo, con sus tokens y su costo | [08](08-evals-y-observabilidad.md) |
| **p50 / p95** | La latencia que no superan el 50 % y el 95 % de las peticiones | [09](09-produccion-y-aws.md) |

## Agente y seguridad

| Término | Qué es | Más en |
|---|---|---|
| **Workflow** | Una secuencia de pasos que decide el código | [06](06-agente-mcp-y-seguridad.md) |
| **Agente** | Un ciclo en el que el LLM decide qué paso sigue | [06](06-agente-mcp-y-seguridad.md) |
| **Tool** | Una función que el LLM puede pedir que se ejecute | [06](06-agente-mcp-y-seguridad.md) |
| **MCP** | *Model Context Protocol*: un protocolo estándar para ofrecer tools a cualquier cliente | [06](06-agente-mcp-y-seguridad.md) |
| **Aprobación humana** | Una pausa para que una persona autorice una acción sensible | [06](06-agente-mcp-y-seguridad.md) |
| **Prompt injection** | Texto que intenta que el modelo obedezca a quien no debe | [06](06-agente-mcp-y-seguridad.md) |
| **Enmascarado** | Sustituir datos personales antes de que salgan del sistema | [06](06-agente-mcp-y-seguridad.md) |
| **RLS** | *Row-Level Security*: la base decide, fila por fila, qué puede ver cada sesión | [06](06-agente-mcp-y-seguridad.md) |
| **Red team** | Atacar el sistema a propósito para encontrar fallas antes que otro | [06](06-agente-mcp-y-seguridad.md) |

## Datos

| Término | Qué es | Más en |
|---|---|---|
| **Transacción** | Un grupo de escrituras que ocurren todas o ninguna | [07](07-modelo-de-datos.md) |
| **ACID** | Atomicidad, consistencia, aislamiento y durabilidad | [07](07-modelo-de-datos.md) |
| **Normalización** | Guardar cada dato una sola vez y referirse a él por su llave | [07](07-modelo-de-datos.md) |
| **Idempotencia** | Repetir una operación no cambia el resultado | [07](07-modelo-de-datos.md) |
| **Outbox** | Guardar el evento en la misma transacción que el dato y publicarlo después | [07](07-modelo-de-datos.md) |
| **Al menos una vez** | Garantía de entrega: un evento puede repetirse, nunca perderse | [07](07-modelo-de-datos.md) |

## Operación

| Término | Qué es | Más en |
|---|---|---|
| **Fábrica de la app** | Una función que construye la aplicación y recibe sus dependencias | [03](03-arquitectura.md) |
| **Lifespan** | El código que corre al arrancar y al apagar la aplicación | [03](03-arquitectura.md) |
| **SSE** | *Server-Sent Events*: una respuesta HTTP abierta que manda eventos de texto | [09](09-produccion-y-aws.md) |
| **Caché semántica** | Reutilizar la respuesta de una pregunta anterior muy parecida | [09](09-produccion-y-aws.md) |
| **Ruteo de modelos** | Elegir el modelo según la dificultad de la pregunta | [09](09-produccion-y-aws.md) |
| **Rate limit** | El máximo de peticiones permitidas en una ventana de tiempo | [09](09-produccion-y-aws.md) |
| **CDK** | Infraestructura de AWS descrita como código | [09](09-produccion-y-aws.md) |
| **Fargate** | Contenedores en AWS sin administrar servidores | [09](09-produccion-y-aws.md) |
| **NAT Gateway** | Salida a internet para subredes privadas; se cobra por hora | [09](09-produccion-y-aws.md) |
