from agentic_runtime.core.query_engine import QueryEngine
from agentic_runtime.core.runtime import build_runtime


def main() -> None:
    runtime = build_runtime()
    engine = QueryEngine(runtime)
    result = engine.run('status del sistema')
    print(result.session_id)
    print(result.answer[:400])


if __name__ == '__main__':
    main()
