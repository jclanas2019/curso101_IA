from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ToolContext:
    session_id: str
    agent_name: str
    cwd: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Tool:
    name: str = 'tool'
    description: str = 'Base tool'

    def run(self, argument: str, context: ToolContext) -> str:
        raise NotImplementedError
