from __future__ import annotations

import shlex
import subprocess
from agentic_runtime.tools.base import Tool, ToolContext

FORBIDDEN_TOKENS = {'rm', 'shutdown', 'reboot', ':(){:|:&};:', 'mkfs', 'dd'}


class BashTool(Tool):
    name = 'bash'
    description = 'Ejecuta comandos bash simples con restricciones básicas.'

    def run(self, argument: str, context: ToolContext) -> str:
        parts = shlex.split(argument)
        if not parts:
            return 'bash: comando vacío'
        if any(token in FORBIDDEN_TOKENS for token in parts):
            return 'bash: comando bloqueado por política básica de seguridad'
        try:
            completed = subprocess.run(
                argument,
                shell=True,
                cwd=context.cwd,
                text=True,
                capture_output=True,
                timeout=20,
            )
            output = completed.stdout.strip()
            err = completed.stderr.strip()
            status = f'[exit={completed.returncode}]'
            if output and err:
                return f'{status}
STDOUT:
{output}

STDERR:
{err}'
            if output:
                return f'{status}
{output}'
            if err:
                return f'{status}
{err}'
            return status
        except subprocess.TimeoutExpired:
            return 'bash: timeout'
