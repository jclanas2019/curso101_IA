from __future__ import annotations

from dataclasses import dataclass
from agentic_runtime.infra.policy import PolicyEngine
from agentic_runtime.tools.base import Tool, ToolContext
from agentic_runtime.tools.bash_tool import BashTool
from agentic_runtime.tools.file_read_tool import FileReadTool
from agentic_runtime.tools.file_write_tool import FileWriteTool
from agentic_runtime.tools.search_tool import SearchTool


@dataclass(slots=True)
class ToolPolicy:
    """Política de acceso por agente (qué tools puede usar)."""
    allowed_tools: set[str]

    def can_use(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools


class ToolRegistry:
    """Registro de tools con doble capa de control de acceso:

    1. ToolPolicy  → qué tools puede usar cada agente (por nombre)
    2. PolicyEngine → qué argumentos/comandos están permitidos (regex)

    La PolicyEngine se pasa al BashTool para que Container la aplique
    en cada ejecución.
    """

    def __init__(self, policy: PolicyEngine | None = None) -> None:
        self._policy_engine = policy or PolicyEngine()
        self._tools: dict[str, Tool] = {}
        for tool in (
            BashTool(policy=self._policy_engine),
            FileReadTool(),
            FileWriteTool(),
            SearchTool(),
        ):
            self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def run(
        self,
        tool_name: str,
        argument: str,
        context: ToolContext,
        policy: ToolPolicy,
    ) -> str:
        if tool_name not in self._tools:
            return f"tool_registry: tool no existe: {tool_name}"
        if not policy.can_use(tool_name):
            return f"tool_registry: acceso denegado a tool '{tool_name}' para agente '{context.agent_name}'"
        return self._tools[tool_name].run(argument, context)

    def help(self) -> str:
        return "\n".join(f"- {name}" for name in self.list_tools())
