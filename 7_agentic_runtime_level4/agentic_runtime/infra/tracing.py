from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Generator

from agentic_runtime.utils.io import write_json
from agentic_runtime.utils.time_utils import utc_now_iso


@dataclass
class Span:
    """Unidad mínima de tracing: un evento con duración."""
    event: str
    data: object
    started_at: str = field(default_factory=utc_now_iso)
    duration_ms: float = 0.0
    node: str = ""
    session_id: str = ""

    def to_dict(self) -> dict:
        return {
            "event": self.event,
            "node": self.node,
            "session_id": self.session_id,
            "started_at": self.started_at,
            "duration_ms": round(self.duration_ms, 2),
            "data": str(self.data)[:500],
        }


class Tracer:
    """Tracer estructurado con spans, persistencia opcional y hooks.

    Compatible con la interfaz de OpenTelemetry:
        - log()   → span puntual
        - span()  → context manager con duración medida

    Si se provee `trace_dir`, persiste cada span como JSON.
    """

    def __init__(self, trace_dir: Path | None = None) -> None:
        self._spans: list[Span] = []
        self._trace_dir = trace_dir
        if trace_dir:
            trace_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def log(self, event: str, data: object, node: str = "", session_id: str = "") -> Span:
        """Registra un span puntual (sin duración)."""
        span = Span(event=event, data=data, node=node, session_id=session_id)
        self._record(span)
        return span

    @contextmanager
    def span(
        self, event: str, node: str = "", session_id: str = ""
    ) -> Generator[Span, None, None]:
        """Context manager que mide la duración del bloque.

        Ejemplo::

            with tracer.span("llm_call", node="llm_node", session_id=sid):
                result = llm.generate(...)
        """
        s = Span(event=event, node=node, session_id=session_id, data="")
        t0 = time.perf_counter()
        try:
            yield s
        finally:
            s.duration_ms = (time.perf_counter() - t0) * 1000
            self._record(s)

    def recent(self, n: int = 20) -> list[dict]:
        """Retorna los últimos n spans como dicts."""
        return [s.to_dict() for s in self._spans[-n:]]

    def for_session(self, session_id: str) -> list[dict]:
        """Filtra spans por session_id."""
        return [s.to_dict() for s in self._spans if s.session_id == session_id]

    def clear(self) -> None:
        self._spans.clear()

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------

    def _record(self, span: Span) -> None:
        self._spans.append(span)
        if self._trace_dir:
            path = self._trace_dir / f"{span.started_at.replace(':', '-')}-{span.event}.json"
            try:
                write_json(path, span.to_dict())
            except Exception:
                pass
