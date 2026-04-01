from __future__ import annotations

from dataclasses import dataclass
from agentic_runtime.config import Settings, get_settings
from agentic_runtime.memory.store import MemoryStore
from agentic_runtime.storage.layout import RuntimeLayout
from agentic_runtime.storage.session_store import SessionStore
from agentic_runtime.storage.job_store import JobStore
from agentic_runtime.tools.registry import ToolRegistry


@dataclass(slots=True)
class RuntimeContainer:
    settings: Settings
    layout: RuntimeLayout
    sessions: SessionStore
    jobs: JobStore
    memory: MemoryStore
    tools: ToolRegistry


def build_runtime() -> RuntimeContainer:
    settings = get_settings()
    layout = RuntimeLayout.from_settings(settings)
    return RuntimeContainer(
        settings=settings,
        layout=layout,
        sessions=SessionStore(layout.sessions),
        jobs=JobStore(layout.jobs),
        memory=MemoryStore(layout.memory),
        tools=ToolRegistry(),
    )
