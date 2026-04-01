from __future__ import annotations

from pathlib import Path
from agentic_runtime.agents.models import AgentSpec
from agentic_runtime.agents.worker import WorkerAgent
from agentic_runtime.memory.store import MemoryStore
from agentic_runtime.tools.registry import ToolPolicy, ToolRegistry


class Coordinator:
    def __init__(self, tool_registry: ToolRegistry, memory_store: MemoryStore, workspaces_root: Path):
        self.tool_registry = tool_registry
        self.memory_store = memory_store
        self.workspaces_root = workspaces_root

    def _ensure_workspace(self, name: str) -> Path:
        path = self.workspaces_root / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _planner(self) -> WorkerAgent:
        spec = AgentSpec(
            name='planner',
            role='Planificación y síntesis',
            workspace=self._ensure_workspace('planner'),
            policy=ToolPolicy(allowed_tools={'search', 'file_read'}),
            can_spawn_subagents=True,
        )
        return WorkerAgent(spec, self.tool_registry, self.memory_store)

    def _coder(self) -> WorkerAgent:
        spec = AgentSpec(
            name='coder',
            role='Operación sobre archivos y shell',
            workspace=self._ensure_workspace('coder'),
            policy=ToolPolicy(allowed_tools={'bash', 'file_read', 'file_write', 'search'}),
        )
        return WorkerAgent(spec, self.tool_registry, self.memory_store)

    def handle(self, prompt: str, session_id: str) -> str:
        planner = self._planner()
        coder = self._coder()

        parts: list[str] = []
        if prompt.lower().startswith('plan') or 'plan' in prompt.lower():
            parts.append('[planner]')
            parts.append(planner.execute(f'search {prompt.replace("plan", "").strip() or "README"}', session_id).summary)
        parts.append('[coder]')
        parts.append(coder.execute(prompt, session_id).summary)
        return '
'.join(parts)
