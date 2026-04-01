from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class PolicyViolation:
    reason: str
    rule: str
    input_fragment: str


@dataclass
class PolicyResult:
    allowed: bool
    violation: PolicyViolation | None = None

    def __bool__(self) -> bool:
        return self.allowed


# Reglas por defecto — lista de (nombre_regla, patrón_regex)
_DEFAULT_RULES: list[tuple[str, str]] = [
    ("shell_destruct",    r"\brm\s+-rf\b"),
    ("shell_destruct",    r"\bmkfs\b"),
    ("shell_destruct",    r"\bdd\b\s+if="),
    ("system_control",   r"\b(shutdown|reboot|halt|poweroff)\b"),
    ("fork_bomb",        r":\(\)\{"),
    ("privilege_escal",  r"\bsudo\b|\bsu\s"),
    ("data_exfil",       r"curl\s+.*\|\s*bash|wget\s+.*\|\s*bash"),
    ("prompt_injection", r"ignore\s+previous\s+instructions"),
]


class PolicyEngine:
    """Motor de políticas de seguridad centralizado.

    Reemplaza los FORBIDDEN_TOKENS dispersos en BashTool y añade
    control a nivel de prompt y tool.

    Uso::

        policy = PolicyEngine()
        result = policy.check_task("rm -rf /")
        if not result:
            print(result.violation.reason)

        # Añadir regla personalizada
        policy.add_rule("no_curl", r"\\bcurl\\b")
    """

    def __init__(
        self,
        extra_rules: list[tuple[str, str]] | None = None,
        blocked_phrases: list[str] | None = None,
    ) -> None:
        self._rules: list[tuple[str, re.Pattern]] = [
            (name, re.compile(pattern, re.IGNORECASE))
            for name, pattern in _DEFAULT_RULES
        ]
        for name, pattern in (extra_rules or []):
            self.add_rule(name, pattern)

        self._blocked_phrases: list[str] = [
            p.lower() for p in (blocked_phrases or [])
        ]

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def add_rule(self, name: str, pattern: str) -> None:
        """Añade una regla regex en tiempo de ejecución."""
        self._rules.append((name, re.compile(pattern, re.IGNORECASE)))

    def check_task(self, text: str) -> PolicyResult:
        """Evalúa un prompt o comando contra todas las reglas.

        Retorna PolicyResult con allowed=True si no hay violaciones.
        """
        for phrase in self._blocked_phrases:
            if phrase in text.lower():
                return PolicyResult(
                    allowed=False,
                    violation=PolicyViolation(
                        reason="frase bloqueada",
                        rule="blocked_phrase",
                        input_fragment=text[:120],
                    ),
                )

        for rule_name, pattern in self._rules:
            m = pattern.search(text)
            if m:
                return PolicyResult(
                    allowed=False,
                    violation=PolicyViolation(
                        reason=f"regla de seguridad: {rule_name}",
                        rule=rule_name,
                        input_fragment=m.group(0)[:80],
                    ),
                )

        return PolicyResult(allowed=True)

    # Alias semántico para compatibilidad con Level 4
    def allow(self, text: str) -> bool:
        return self.check_task(text).allowed
