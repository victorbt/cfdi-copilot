# 10 · Decisiones

> **Estado:** vivo · se agrega una fila cada vez que se elige algo · **Lectura:** de consulta ·
> [Índice](README.md) · Anterior: [09 · Producción y AWS](09-produccion-y-aws.md) · Siguiente: [Glosario](glosario.md)

Cada fila dice qué se eligió, en lugar de qué, por qué y **qué se sacrificó**. Una decisión sin
costo aceptado no es una decisión: es una preferencia.

## Cómo leer el registro

| Estado | Significa |
|---|---|
| **Vigente** | Ya está en el código y los tests lo sostienen |
| **En construcción** | Se programa en la semana en curso |
| **Planeada** | Diseñada; se confirma con números la semana indicada, o se cambia |

Las decisiones que todavía no se toman están al final de los documentos
[05](05-flujos-rag.md#decisiones-abiertas) y [09](09-produccion-y-aws.md#decisiones-abiertas).

## Base del proyecto

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D1** · `uv` para entorno y dependencias | pip con venv, Poetry | Un solo binario, lockfile reproducible e instala también Python | Herramienta más joven que las alternativas | Vigente |
| **D2** · Modelos Pydantic estrictos e inmutables | Diccionarios, dataclasses o modelos permisivos | Un campo de más que invente el LLM es un error, no un dato ignorado; un comprobante validado ya no cambia | Para modificar hay que crear otro objeto | Vigente |
| **D3** · Dinero en `Decimal` y `NUMERIC` | `float` | Los totales deben cuadrar al centavo, y `0.1 + 0.2` no da `0.3` en `float` | Hay que cuidar redondeo y serialización | Vigente |
| **D4** · Nombres del Anexo 20 como alias | Un solo juego de nombres | El JSON habla el idioma del estándar y el código el de Python | Dos nombres por campo | Vigente |
| **D5** · Tipos estrictos (`mypy --strict`) y `ruff` desde el primer día | Agregar tipos después | Los errores aparecen antes de ejecutar | Fricción con librerías sin tipos | Vigente |
| **D6** · Solo datos sintéticos y documentos públicos | Datos reales anonimizados | El repositorio es público y debe poder serlo siempre | Las facturas sintéticas son más limpias que las reales: los números de extracción salen optimistas | Vigente |

## LLM y extracción

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D7** · Structured outputs, más validación propia, más un reintento de reparación | Pedir JSON en el prompt y parsear; confiar solo en el schema | El schema garantiza la forma, no la verdad: que los totales cuadren lo decide el código | Una llamada extra cuando falla; el schema no expresa reglas entre campos | En construcción |
| **D8** · Ollama solo para desarrollar | Ollama para todo, o API para todo | Iterar no cuesta; pero un modelo local chico no representa lo que correría en producción | Dos entornos que se comportan distinto; lo medido en local no se reporta | Vigente |
| **D9** · Cliente propio sobre `httpx` | SDK del proveedor o una capa de abstracción | Se ve todo lo que viaja: payload, timeouts y tokens | Hay que mantenerlo; la interfaz común se extrae cuando llegue el segundo proveedor | Vigente |
| **D10** · Fábrica de la app con `lifespan` y un cliente HTTP de larga vida | Cliente global al importar, o uno por petición | El LLM se inyecta, así que los tests no necesitan red; una sola reserva de conexiones | Algo más de ceremonia al arrancar | En construcción |
| **D11** · Timeouts explícitos por fase | El timeout único por omisión | Conectar debe fallar en segundos; leer la respuesta de un LLM puede tardar un minuto | Cuatro números que ajustar | Vigente |

## Datos y recuperación

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D12** · Un solo Postgres con pgvector | Base vectorial dedicada junto a Postgres | Una sola pieza que operar; facturas, eventos, texto y vectores en la misma transacción y con los mismos filtros | A gran escala una base dedicada rinde más; el índice compite por memoria con lo demás | Planeada · semana 2 |
| **D13** · Búsqueda híbrida fusionada con RRF | Solo vectores, solo texto, o sumar puntajes con pesos | Las claves exactas (`G03`, `601`) las encuentra el texto y las paráfrasis los vectores; RRF usa posiciones, así que no hay que igualar escalas | Dos búsquedas por pregunta | Planeada · semana 2 |
| **D14** · Dos columnas de embeddings mientras dura la comparación | Reindexar todo para probar cada modelo | Los dos modelos se miden con el mismo golden set, lado a lado | Doble almacenamiento y doble índice, de forma temporal | Planeada · semana 2 |
| **D15** · Citas obligatorias y permiso de abstenerse | Contestar siempre | En un tema fiscal, una respuesta inventada es peor que ninguna | Más respuestas "no lo sé"; hay que medir que no se pase de cauteloso | Planeada · semana 2 |
| **D16** · Tablas normalizadas con una copia histórica a propósito | Todo normalizado, o todo en un JSON | La factura es un documento histórico; los datos del contribuyente cambian | Datos repetidos a conciencia | Planeada · semana 1 |
| **D17** · Outbox en la misma transacción | Publicar el evento después del `COMMIT` | La factura y su aviso existen juntos o no existen | Entrega al menos una vez: quien consume debe ser idempotente; un proceso más | Planeada · semana 1 |
| **D18** · Idempotencia por huella del texto de entrada | Sin llave, o una llave que mande el cliente | No hay timbre en datos sintéticos, y el mismo texto no debe crear dos facturas | Un espacio de más cambia la huella: hay que normalizar antes de calcularla | Planeada · semana 1 |

## Calidad y observabilidad

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D19** · Evals en CI con umbral | Revisar a mano de vez en cuando | La calidad de un sistema con LLM baja sin que nada truene | CI más lento, con costo por corrida y algo de ruido | Planeada · semana 3 |
| **D20** · Golden set chico, escrito y verificado a mano, dentro del repo | Cientos de preguntas generadas por un LLM | Cada pregunta se comprobó contra el documento y se versiona con el código | Con 30 preguntas, una diferencia pequeña es ruido | Planeada · semana 2 |
| **D21** · Ragas más un juez propio calibrado | Solo métricas de librería, o solo un juez propio | Métricas conocidas, más un juez cuya rúbrica se entiende y se comparó con etiquetas humanas | Mantener la rúbrica y repetir la calibración si cambia el modelo | Planeada · semana 3 |
| **D22** · Langfuse Cloud | Alojarlo uno mismo, o solo logs | Nada que operar; trazas, costo, prompts y datasets en un solo lugar | Los datos salen a un tercero: solo sintéticos, y enmascarados antes de enviarse | Planeada · semana 1 |

## Agente y seguridad

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D23** · Workflow por omisión; agente solo donde no alcanza | Agente para todo | Un workflow es predecible, barato y fácil de evaluar | Menos flexible ante tareas no previstas | Planeada · semana 5 |
| **D24** · LangGraph para el agente | Un ciclo escrito a mano | Estado explícito y puntos de control para pausar y pedir aprobación humana | Una dependencia grande, con su curva y sus cambios de versión | Planeada · semana 5 |
| **D25** · Tools expuestas por MCP, con versiones fijas | Funciones internas del agente | Las mismas tools sirven al agente y a clientes externos | Protocolo joven; un proceso más que arrancar | Planeada · semanas 1 y 5 |
| **D26** · SQL de solo lectura: rol sin escritura, tiempo máximo, `LIMIT` forzado y permisos por fila | Pedirle al LLM en el prompt que se porte bien | La regla vive en la base y se cumple aunque el LLM genere otra cosa | El agente no puede escribir; una consulta legítima pero lenta se corta | Planeada · semanas 5 y 6 |
| **D27** · Enmascarar datos personales antes del LLM y de las trazas | Enmascarar solo los logs, o nada por ser datos sintéticos | Es la defensa que haría falta con datos reales | Falsos positivos que degradan alguna respuesta; algo de latencia | Planeada · semana 6 |

## Operación

| Decisión | En lugar de | Por qué | Costo aceptado | Estado |
|---|---|---|---|---|
| **D28** · Transmitir solo texto ya validado | Transmitir cada token | Mostrar texto sin validar rompe la promesa del sistema | Más lógica en el servidor; el primer texto tarda un poco más | Planeada · semana 7 |
| **D29** · Versión del corpus y del prompt dentro de la llave de caché | Borrar la caché a mano cuando algo cambia | Las entradas viejas dejan de coincidir solas | Tras cada cambio la caché arranca vacía | Planeada · semana 7 |
| **D30** · Fargate y RDS, sin NAT Gateway | Subredes privadas con NAT, o *VPC endpoints* | El contenedor necesita salir a internet y el NAT se cobra por hora | La tarea tiene IP pública, protegida por su *security group* | Planeada · semana 8 |
| **D31** · Desplegar, medir y destruir el mismo día | Dejar el servicio prendido | El objetivo es un costo real medido, no una demo permanente | No queda una URL pública que enseñar | Planeada · semana 8 |

## Cómo se agrega una decisión

1. Se escribe la fila **antes** de programar, con estado *Planeada*.
2. Al programarla pasa a *En construcción*, y a *Vigente* cuando los tests la sostienen.
3. Si una medición la contradice, la fila no se borra: se marca como reemplazada y se agrega la
   nueva debajo, con el número que la motivó.

## Comprueba que lo entendiste

<details>
<summary>1. Si el LLM ya responde con un JSON Schema, ¿por qué se valida otra vez con Pydantic?</summary>

Porque el schema garantiza la forma, no la verdad. Un JSON puede tener todos los campos con el tipo
correcto y aun así traer un total que no es la suma de sus conceptos. Esa regla solo la puede
revisar el código.
</details>

<details>
<summary>2. ¿Qué se sacrifica al guardar todo en un solo Postgres?</summary>

Rendimiento a gran escala: una base vectorial dedicada rinde más con muchos millones de vectores, y
el índice compite por memoria con las demás tablas. Se acepta porque hay una sola pieza que operar y
porque facturas, eventos y vectores comparten transacciones y filtros. La decisión se revisa cuando
una medición lo justifique.
</details>

<details>
<summary>3. ¿Por qué los permisos por RFC viven en la base de datos y no en el prompt?</summary>

Porque una instrucción en el prompt es una sugerencia que el LLM puede ignorar, o que un atacante
puede anular con una inyección. Una política en la base se cumple sin importar qué consulta genere
el modelo.
</details>
