from __future__ import annotations

from dataclasses import dataclass
from agentic_runtime.agents.models import AgentSpec
from agentic_runtime.memory.store import MemoryStore
from agentic_runtime.tools.base import ToolContext
from agentic_runtime.tools.registry import ToolRegistry


@dataclass(slots=True)
class WorkerResult:
    agent_name: str
    summary: str


class WorkerAgent:
    def __init__(self, spec: AgentSpec, tool_registry: ToolRegistry, memory_store: MemoryStore):
        self.spec = spec
        self.tool_registry = tool_registry
        self.memory_store = memory_store

    def execute(self, task: str, session_id: str) -> WorkerResult:
        lowered = task.lower().strip()
        context = ToolContext(session_id=session_id, agent_name=self.spec.name, cwd=str(self.spec.workspace))

        if lowered.startswith('bash '):
            summary = self.tool_registry.run('bash', task[5:], context, self.spec.policy)
        elif lowered.startswith('read '):
            summary = self.tool_registry.run('file_read', task[5:], context, self.spec.policy)
        elif lowered.startswith('write '):
            summary = self.tool_registry.run('file_write', task[6:], context, self.spec.policy)
        elif lowered.startswith('search '):
            summary = self.tool_registry.run('search', task[7:], context, self.spec.policy)
        else:
            summary = f'{self.spec.name}: tarea interpretada sin tool directa -> {task}'

        self.memory_store.put('local', f'last_result_{self.spec.name}', summary[:2000])
        return WorkerResult(agent_name=self.spec.name, summary=summary)
