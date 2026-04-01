"""
Smoke test completo del runtime Level 4.
Ejecutar: AGENTIC_DEFAULT_MODE=mock python -m agentic_runtime.tests_smoke
"""
from __future__ import annotations

from agentic_runtime.core.runtime import build_runtime
from agentic_runtime.core.query_engine import QueryEngine


def _sep(title: str) -> None:
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print('─'*55)


def main() -> None:
    runtime = build_runtime()
    engine = QueryEngine(runtime)

    # ── 1. Query normal ──────────────────────────────────────────
    _sep("1. Query normal")
    r = engine.run("status del sistema")
    print(f"session : {r.session_id[:8]}...")
    print(f"blocked : {r.blocked}")
    print(r.answer[:300])

    # ── 2. VectorDB — buscar justo después de indexar ────────────
    _sep("2. VectorDB semántico (post-query 1)")
    results = runtime.vector.search("status sistema", top_k=3)
    print(f"entries en VectorDB : {runtime.vector.count()}")
    print(f"resultados 'status sistema': {len(results)}")
    for res in results:
        print(f"  [{res.score:.3f}] {res.entry.key}")

    # ── 3. Segunda query — memoria se enriquece ──────────────────
    _sep("3. Plan (misma sesión)")
    r2 = engine.run("plan de trabajo para hoy", session_id=r.session_id)
    print(r2.answer[:250])

    # ── 4. PolicyEngine bloquea comandos destructivos ────────────
    _sep("4. PolicyEngine — rm -rf bloqueado")
    r3 = engine.run("bash rm -rf /tmp/test", session_id=r.session_id)
    print(f"blocked     : {r3.blocked}")
    print(f"block_reason: {r3.block_reason}")
    print(r3.answer)

    # ── 5. PolicyEngine — sudo bloqueado ────────────────────────
    _sep("5. PolicyEngine — sudo bloqueado")
    r4 = engine.run("ejecuta sudo apt update", session_id=r.session_id)
    print(f"blocked: {r4.blocked} | reason: {r4.block_reason}")

    # ── 6. Tracer spans ──────────────────────────────────────────
    _sep("6. Tracer — últimos 10 spans")
    for s in runtime.tracer.recent(10):
        ms = s["duration_ms"]
        print(f"  [{s['node']:12}] {s['event']:<22} {ms:.1f}ms")

    # ── 7. EventBus ──────────────────────────────────────────────
    _sep("7. EventBus — pendientes")
    print(f"Eventos pendientes (ya despachados): {runtime.bus.pending()}")

    # ── 8. Grafo LangGraph ───────────────────────────────────────
    _sep("8. Grafo LangGraph")
    g = engine._graph.get_graph()
    print("Nodos:", list(g.nodes.keys()))
    for e in g.edges:
        print(f"  {e[0]:14} ─▶  {e[1]}")

    print("\n" + "═"*55)
    print("  SMOKE TEST COMPLETO OK")
    print("═"*55 + "\n")


if __name__ == "__main__":
    main()
