from __future__ import annotations

from pathlib import Path
from agentic_runtime.tools.base import Tool, ToolContext


class FileReadTool(Tool):
    name = 'file_read'
    description = 'Lee un archivo de texto desde el workspace actual.'

    def run(self, argument: str, context: ToolContext) -> str:
        path = (Path(context.cwd) / argument).resolve() if not Path(argument).is_absolute() else Path(argument)
        if not path.exists():
            return f'file_read: no existe {path}'
        if path.is_dir():
            return f'file_read: {path} es un directorio'
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return 'file_read: archivo no es texto UTF-8'
