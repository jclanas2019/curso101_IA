# Agentic Runtime Level 2

Maqueta avanzada en Python de un runtime agentico inspirado en la arquitectura analizada.

## Incluye

- CLI interactiva y ejecución por comando
- QueryEngine stateful
- Coordinador + subagentes
- Registro de tools con permisos por agente
- Memoria persistente por `user`, `project` y `local`
- Sesiones persistentes y transcript por conversación
- Jobs en background con PID, logs y control (`ps`, `logs`, `kill`)
- Scheduler simple con jobs persistidos
- Workspaces aislados por subagente
- Capa opcional de LLM vía OpenAI Responses API
- Configuración por `.env`

## Estructura

```text
main.py
agentic_runtime/
  agents/
  cli/
  core/
  llm/
  memory/
  scheduler/
  storage/
  tools/
  utils/
```

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Variables de entorno

- `OPENAI_API_KEY`
- `OPENAI_MODEL` (por defecto `gpt-4.1-mini`)
- `AGENTIC_DATA_DIR` (por defecto `./runtime_data`)
- `AGENTIC_DEFAULT_MODE` (`mock` u `openai`)

## Uso rápido

### CLI interactiva

```bash
python main.py interactive
```

### Ejecutar un prompt puntual

```bash
python main.py run "resume el estado del sistema"
```

### Jobs en background

```bash
python main.py bg start "analiza README.md"
python main.py bg ps
python main.py bg logs <job_id>
python main.py bg kill <job_id>
```

### Scheduler

```bash
python main.py cron add heartbeat 60 "muestra estado"
python main.py cron list
python main.py cron run-once
```

## Notas

- El modo `mock` funciona sin API externa.
- El `BashTool` restringe comandos peligrosos obvios, pero sigue siendo una maqueta. No lo expongas sin sandbox real.
- El scheduler es deliberadamente simple: persiste definición de jobs y los ejecuta en un loop cuando se llama `cron run-loop`.

## Próximas extensiones recomendadas

1. Aislamiento real con procesos/containers por subagente.
2. Vector store opcional para recuperación semántica.
3. Cola de eventos con webhooks.
4. Policy engine más fino por tool/acción.
5. Observabilidad con trazas estructuradas.
