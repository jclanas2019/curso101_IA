from __future__ import annotations

from pathlib import Path
from agentic_runtime.tools.base import Tool, ToolContext


class SearchTool(Tool):
    name = "search"
    description = "Busca una cadena en archivos .py, .md, .txt del workspace."

    def run(self, argument: str, context: ToolContext) -> str:
        needle = argument.strip()
        if not needle:
            return "search: término vacío"
        matches: list[str] = []
        for path in Path(context.cwd).rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".txt", ".json"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, start=1):
                if needle.lower() in line.lower():
                    matches.append(f"{path}:{i}: {line.strip()}")
            if len(matches) >= 50:
                break
        return "\n".join(matches) if matches else "search: sin coincidencias"
