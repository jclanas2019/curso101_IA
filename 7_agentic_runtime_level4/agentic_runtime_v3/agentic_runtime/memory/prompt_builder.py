from __future__ import annotations

from agentic_runtime.memory.store import MemoryStore


class MemoryPromptBuilder:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store

    def build(self) -> str:
        sections: list[str] = []
        for scope in ("user", "project", "local"):
            items = self.memory_store.list_scope(scope)
            if not items:
                continue
            sections.append(f"[{scope.upper()} MEMORY]")
            for item in items[:10]:
                sections.append(f"- {item['key']}: {item['value']}")
        return "\n".join(sections).strip()
