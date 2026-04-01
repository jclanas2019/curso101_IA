from __future__ import annotations

from pathlib import Path
from agentic_runtime.tools.base import Tool, ToolContext


class FileWriteTool(Tool):
    name = 'file_write'
    description = 'Escribe un archivo. Formato: ruta::contenido'

    def run(self, argument: str, context: ToolContext) -> str:
        if '::' not in argument:
            return 'file_write: usa formato ruta::contenido'
        raw_path, content = argument.split('::', 1)
        path = (Path(context.cwd) / raw_path.strip()).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return f'file_write: escrito {path}'
