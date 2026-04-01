from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from agentic_runtime.tools.registry import ToolPolicy


@dataclass(slots=True)
class AgentSpec:
    name: str
    role: str
    workspace: Path
    policy: ToolPolicy
    can_spawn_subagents: bool = False
    metadata: dict[str, str] = field(default_factory=dict)
