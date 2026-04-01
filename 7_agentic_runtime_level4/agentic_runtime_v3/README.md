# Agentic Runtime Level 4 — LangGraph + Infra Layer

Runtime agentico en Python con orquestación **LangGraph**, modelo
**gpt-4.1-mini** (vía `.env`) e infraestructura completa de producción.

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                     QueryEngine                         │
│                                                         │
│  PolicyEngine ──► BLOCK (❌ devuelve sin ejecutar)      │
│       │                                                 │
│  EventBus.publish("user.input")                         │
│       │                                                 │
│  ┌────▼────────────────────────────────────┐            │
│  │         Grafo LangGraph                 │            │
│  │                                         │            │
│  │  START                                  │            │
│  │    │                                    │            │
│  │    ▼                                    │            │
│  │  vector_node  ← VectorDB TF-IDF         │            │
│  │    │                                    │            │
│  │    ▼                                    │            │
│  │  planner      ← SearchTool + Tracer     │            │
│  │    │                                    │            │
│  │    ▼                                    │            │
│  │  coder        ← Container + Tracer      │            │
│  │    │                                    │            │
│  │    ▼                                    │            │
│  │  llm_node     ← gpt-4.1-mini + Tracer  │            │
│  │    │                                    │            │
│  │    ▼                                    │            │
│  │  assembler    ← combina respuesta final │            │
│  │    │                                    │            │
│  │   END                                   │            │
│  └─────────────────────────────────────────┘            │
│       │                                                 │
│  EventBus.publish("agent.response")                     │
│  MemoryStore.put() → VectorDB (índice automático)       │
└─────────────────────────────────────────────────────────┘
```

## Módulos nuevos (Level 4)

```
agentic_runtime/
  infra/
    queue.py       EventBus tipado — tópicos + suscriptores
    tracing.py     Tracer con spans medidos (OpenTelemetry-ready)
    policy.py      PolicyEngine centralizado — regex + frases bloqueadas
  isolation/
    container.py   Container — frontera única con subprocess + PolicyEngine
  memory/
    vector_db.py   VectorDB — TF-IDF (enchufable a FAISS / Chroma)
```

## Componentes existentes mejorados

| Módulo | Mejora |
|--------|--------|
| `tools/bash_tool.py` | Usa `Container` — ya no llama subprocess directamente |
| `tools/registry.py` | Pasa `PolicyEngine` al `BashTool` |
| `core/runtime.py` | `RuntimeContainer` incluye `bus`, `tracer`, `policy`, `vector` |
| `core/query_engine.py` | Verifica policy, publica eventos, conecta VectorDB a MemoryStore |
| `graph/nodes.py` | Cada nodo emite spans con duración medida |
| `graph/builder.py` | Nuevo nodo `vector_node` al inicio del pipeline |
| `graph/state.py` | `AgentState` incluye `vector_context` y `trace_spans` |
| `memory/store.py` | `MemoryStore.put()` indexa automáticamente en VectorDB |
| `cli/app.py` | Nuevos comandos `vsearch` y `trace` |

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Variables de entorno (`.env`)

| Variable               | Default          | Descripción                        |
|------------------------|------------------|------------------------------------|
| `OPENAI_API_KEY`       | —                | API key de OpenAI                  |
| `OPENAI_MODEL`         | `gpt-4.1-mini`   | Modelo a usar                      |
| `AGENTIC_DATA_DIR`     | `./runtime_data` | Directorio de persistencia         |
| `AGENTIC_DEFAULT_MODE` | `mock`           | `mock` (sin API) u `openai`        |

## Uso

```bash
# REPL interactivo
python main.py interactive

# Prompt directo
python main.py run "resume el estado del sistema"

# Búsqueda semántica en VectorDB
python main.py vsearch "última respuesta del agente" --top-k 5

# Inspección de trazas
python main.py trace recent
python main.py trace session <session_id>

# Jobs en background
python main.py bg start "analiza README.md"
python main.py bg ps
python main.py bg logs <job_id>

# Scheduler
python main.py cron add heartbeat 60 "muestra estado"
python main.py cron run-once
```

## Extensiones recomendadas

| Componente | Integración |
|---|---|
| `VectorDB` | Sustituir `KeywordVectorBackend` por `FAISSBackend` o `ChromaBackend` |
| `EventBus` | Sustituir `Queue` en memoria por cliente Redis/NATS |
| `Tracer` | Añadir exporter OTLP para Jaeger / Grafana Tempo |
| `Container` | Sustituir `subprocess` por SDK de Docker para aislamiento real |
| `PolicyEngine` | Cargar reglas desde YAML/BD en lugar de código |
