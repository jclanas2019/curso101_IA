from __future__ import annotations

import subprocess
from dataclasses import dataclass

from agentic_runtime.infra.policy import PolicyEngine, PolicyResult


@dataclass
class ExecResult:
    stdout: str
    stderr: str
    exit_code: int
    blocked: bool = False
    block_reason: str = ""

    def as_text(self) -> str:
        if self.blocked:
            return f"container: bloqueado — {self.block_reason}"
        status = f"[exit={self.exit_code}]"
        parts = [status]
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(f"STDERR:\n{self.stderr}")
        return "\n".join(parts)


class Container:
    """Capa de aislamiento de ejecución de comandos shell.

    Actúa como frontera entre el agente y el sistema operativo:
    - Aplica PolicyEngine antes de ejecutar
    - Limita timeout
    - Captura stdout/stderr por separado
    - Diseñado para ser reemplazado por DockerContainer en producción

    Uso::

        container = Container(policy=PolicyEngine())
        result = container.exec("ls -la")
        print(result.as_text())
    """

    DEFAULT_TIMEOUT = 20  # segundos

    def __init__(
        self,
        policy: PolicyEngine | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        cwd: str | None = None,
    ) -> None:
        self._policy = policy or PolicyEngine()
        self._timeout = timeout
        self._cwd = cwd

    def exec(self, cmd: str, cwd: str | None = None) -> ExecResult:
        """Ejecuta un comando shell tras pasar la política de seguridad."""
        policy_result: PolicyResult = self._policy.check_task(cmd)
        if not policy_result:
            return ExecResult(
                stdout="",
                stderr="",
                exit_code=1,
                blocked=True,
                block_reason=policy_result.violation.reason
                if policy_result.violation
                else "política de seguridad",
            )

        work_dir = cwd or self._cwd
        try:
            completed = subprocess.run(
                cmd,
                shell=True,
                cwd=work_dir,
                text=True,
                capture_output=True,
                timeout=self._timeout,
            )
            return ExecResult(
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
                exit_code=completed.returncode,
            )
        except subprocess.TimeoutExpired:
            return ExecResult(
                stdout="",
                stderr="timeout expirado",
                exit_code=124,
            )
        except Exception as exc:
            return ExecResult(
                stdout="",
                stderr=str(exc),
                exit_code=1,
            )
