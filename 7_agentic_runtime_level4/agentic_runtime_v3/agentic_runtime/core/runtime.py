from __future__ import annotations

from dataclasses import dataclass
from agentic_runtime.config import Settings, get_settings
from agentic_runtime.infra.policy import PolicyEngine
from agentic_runtime.infra.queue import EventBus
from agentic_runtime.infra.tracing import Tracer
from agentic_runtime.memory.store import MemoryStore
from agentic_runtime.memory.vector_db import VectorDB
from agentic_runtime.storage.layout import RuntimeLayout
from agentic_runtime.storage.session_store import SessionStore
from agentic_runtime.storage.job_store import JobStore
from agentic_runtime.tools.registry import ToolRegistry


@dataclass(slots=True)
class RuntimeContainer:
    """Contenedor de todas las dependencias del runtime.

    Componentes Level 2/3:
        settings, layout, sessions, jobs, memory, tools

    Componentes Level 4 (nuevos):
        bus     → EventBus tipado con suscriptores
        tracer  → Tracer con spans estructurados (OpenTelemetry-ready)
        policy  → PolicyEngine centralizado (regex + frases bloqueadas)
        vector  → VectorDB semántica (TF-IDF, enchufable a FAISS/Chroma)
    """
    settings: Settings
    layout: RuntimeLayout
    sessions: SessionStore
    jobs: JobStore
    memory: MemoryStore
    tools: ToolRegistry
    # --- Level 4 ---
    bus: EventBus
    tracer: Tracer
    policy: PolicyEngine
    vector: VectorDB


def build_runtime() -> RuntimeContainer:
    settings = get_settings()
    layout = RuntimeLayout.from_settings(settings)
    policy = PolicyEngine()
    return RuntimeContainer(
        settings=settings,
        layout=layout,
        sessions=SessionStore(layout.sessions),
        jobs=JobStore(layout.jobs),
        memory=MemoryStore(layout.memory),
        tools=ToolRegistry(policy=policy),
        # Level 4
        bus=EventBus(),
        tracer=Tracer(trace_dir=layout.root / "traces"),
        policy=policy,
        vector=VectorDB(),
    )
