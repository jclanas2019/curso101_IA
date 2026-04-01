# Agentic Runtime Level 4

Runtime agentico en Python con LangGraph, memoria semántica, bus de eventos,
tracing estructurado y aislamiento de ejecución.

## Arquitectura del grafo (LangGraph)

```
START
  │
  ▼
vector_node  ← recupera contexto semántico (VectorDB / TF-IDF)
  │
  ▼
planner      ← busca contexto en archivos (SearchTool) + span de tracing
  │
  ▼
coder        ← opera sobre archivos / shell via Container + PolicyEngine
  │
  ▼
llm_node     ← genera respuesta con gpt-4.1-mini (o mock) + span
  │
  ▼
assembler    ← combina LLM answer + resultados de agentes
  │
  ▼
 END
```

## Módulos

```text
agentic_runtime/
  agents/          coordinador + worker agents
  cli/             CLI con comandos: run, interactive, bg, memory,
                   vsearch, trace, cron
  core/            query_engine, runtime container, background workers
  graph/           state.py, nodes.py, builder.py  (LangGraph)
  infra/           queue.py (EventBus), tracing.py (Tracer),
                   policy.py (PolicyEngine)
  isolation/       container.py (aislamiento de subprocess)
  llm/             base, mock_client, openai_client (chat.completions)
  memory/          store.py, vector_db.py (TF-IDF → FAISS/Chroma)
  scheduler/       engine + store de cron jobs
  storage/         layout, session_store, job_store
  tools/           bash, file_read, file_write, search + registry
  utils/           io, time_utils
```

## Componentes Level 4 (nuevos vs Level 3)

| Componente     | Archivo                  | Rol                                                  |
|----------------|--------------------------|------------------------------------------------------|
| EventBus       | infra/queue.py           | Bus tipado con suscriptores por tópico               |
| Tracer         | infra/tracing.py         | Spans con duración, persistibles, OpenTelemetry-ready|
| PolicyEngine   | infra/policy.py          | Reglas regex centralizadas (reemplaza FORBIDDEN_TOKENS)|
| VectorDB       | memory/vector_db.py      | Memoria semántica TF-IDF, enchufable a FAISS/Chroma  |
| Container      | isolation/container.py   | Frontera única con el SO; aplica PolicyEngine        |

## Cómo se integran

- **PolicyEngine** es instanciada en `build_runtime()` y compartida por
  `ToolRegistry → BashTool → Container` y por `QueryEngine` (bloquea prompts).
- **VectorDB** se conecta a `MemoryStore.attach_vector_db()`: cada `put()`
  indexa el valor automáticamente para búsqueda semántica posterior.
- **Tracer** se pasa a `build_graph()`: cada nodo LangGraph emite spans
  con duración medida via context manager.
- **EventBus** recibe `user.input` y `agent.response` en cada `run()`,
  y despacha todos los suscriptores tras el grafo.
- **Container** reemplaza el `subprocess.run` crudo en `BashTool`.

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY si usas modo openai
```

## Variables de entorno

| Variable               | Default          | Descripción                       |
|------------------------|------------------|-----------------------------------|
| `OPENAI_API_KEY`       | —                | API key de OpenAI                 |
| `OPENAI_MODEL`         | `gpt-4.1-mini`   | Modelo de chat completions        |
| `AGENTIC_DATA_DIR`     | `./runtime_data` | Directorio de persistencia        |
| `AGENTIC_DEFAULT_MODE` | `mock`           | `mock` (sin API) u `openai`       |

## Uso

```bash
# Prompt único (modo mock sin API key)
python main.py run "resume el estado del sistema"

# REPL interactivo
python main.py interactive

# Búsqueda semántica en VectorDB
python main.py vsearch "último request del usuario"

# Inspección de trazas
python main.py trace recent
python main.py trace session <session_id>

# Jobs en background
python main.py bg start "analiza README.md"
python main.py bg ps

# Scheduler
python main.py cron add heartbeat 60 "muestra estado"
python main.py cron run-once
```

## Próximas extensiones

1. **Docker** en `Container.exec()` — reemplazar `subprocess` por `docker run`.
2. **FAISS/Chroma** — implementar `VectorBackend` con embeddings reales.
3. **Redis/NATS** — reemplazar `EventBus` por bus distribuido.
4. **OpenTelemetry** — exportar spans del `Tracer` a Jaeger/Grafana.
5. **LangSmith** — habilitar `LANGCHAIN_TRACING_V2=true` para trazas del grafo.
6. **human-in-the-loop** — `interrupt_before` en LangGraph para aprobación humana.
