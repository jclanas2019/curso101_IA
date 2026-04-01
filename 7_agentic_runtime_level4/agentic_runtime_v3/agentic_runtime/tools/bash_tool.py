from __future__ import annotations

from agentic_runtime.isolation.container import Container
from agentic_runtime.infra.policy import PolicyEngine
from agentic_runtime.tools.base import Tool, ToolContext


class BashTool(Tool):
    """Ejecuta comandos bash pasando por Container + PolicyEngine.

    El subprocess ya no se llama directamente desde aquí — Container
    es la única frontera con el sistema operativo, aplicando la
    PolicyEngine centralizada antes de ejecutar cualquier comando.
    """

    name = "bash"
    description = "Ejecuta comandos bash simples (filtrados por PolicyEngine)."

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self._container = Container(policy=policy or PolicyEngine())

    def run(self, argument: str, context: ToolContext) -> str:
        if not argument.strip():
            return "bash: comando vacío"
        result = self._container.exec(argument, cwd=context.cwd)
        return result.as_text()
