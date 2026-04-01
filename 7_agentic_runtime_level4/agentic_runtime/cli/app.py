from __future__ import annotations

import argparse
import json

from agentic_runtime.core.background_manager import BackgroundManager
from agentic_runtime.core.query_engine import QueryEngine
from agentic_runtime.core.runtime import build_runtime
from agentic_runtime.scheduler.engine import SchedulerEngine
from agentic_runtime.scheduler.store import SchedulerStore


def interactive(engine: QueryEngine) -> None:
    session_id = None
    print("Modo interactivo. Escribe 'exit' para salir.")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        result = engine.run(user_input, session_id=session_id)
        session_id = result.session_id
        print(f"[session_id] {result.session_id}")
        if result.blocked:
            print(f"❌ Bloqueado: {result.block_reason}")
        else:
            print(result.answer)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentic-runtime")
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    run_cmd = sub.add_parser("run", help="Ejecuta un prompt y sale")
    run_cmd.add_argument("prompt")
    run_cmd.add_argument("--session-id", default=None)

    # interactive
    sub.add_parser("interactive", help="Modo REPL interactivo")

    # bg
    bg = sub.add_parser("bg", help="Jobs en background")
    bg_sub = bg.add_subparsers(dest="bg_command", required=True)
    bg_start = bg_sub.add_parser("start")
    bg_start.add_argument("prompt")
    bg_sub.add_parser("ps")
    bg_logs = bg_sub.add_parser("logs")
    bg_logs.add_argument("job_id")
    bg_kill = bg_sub.add_parser("kill")
    bg_kill.add_argument("job_id")

    # memory
    mem = sub.add_parser("memory", help="Gestión de memoria")
    mem_sub = mem.add_subparsers(dest="memory_command", required=True)
    mem_put = mem_sub.add_parser("put")
    mem_put.add_argument("scope", choices=["user", "project", "local"])
    mem_put.add_argument("key")
    mem_put.add_argument("value")
    mem_list = mem_sub.add_parser("list")
    mem_list.add_argument("scope", choices=["user", "project", "local"])

    # vsearch — búsqueda semántica en VectorDB
    vs = sub.add_parser("vsearch", help="Búsqueda semántica en VectorDB")
    vs.add_argument("query")
    vs.add_argument("--top-k", type=int, default=5)

    # trace — inspección de spans del Tracer
    tr = sub.add_parser("trace", help="Inspección de trazas")
    tr_sub = tr.add_subparsers(dest="trace_command", required=True)
    tr_sub.add_parser("recent")
    tr_session = tr_sub.add_parser("session")
    tr_session.add_argument("session_id")

    # cron
    cron = sub.add_parser("cron", help="Scheduler de jobs")
    cron_sub = cron.add_subparsers(dest="cron_command", required=True)
    cron_add = cron_sub.add_parser("add")
    cron_add.add_argument("name")
    cron_add.add_argument("every_seconds", type=int)
    cron_add.add_argument("prompt")
    cron_sub.add_parser("list")
    cron_del = cron_sub.add_parser("delete")
    cron_del.add_argument("name")
    cron_sub.add_parser("run-once")
    cron_loop = cron_sub.add_parser("run-loop")
    cron_loop.add_argument("--sleep-seconds", type=int, default=5)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    runtime = build_runtime()
    engine = QueryEngine(runtime)
    bg = BackgroundManager(runtime)
    scheduler_store = SchedulerStore(runtime.layout.scheduler)
    scheduler_engine = SchedulerEngine(runtime)

    if args.command == "interactive":
        interactive(engine)
        return

    if args.command == "run":
        result = engine.run(args.prompt, session_id=args.session_id)
        print(f"[session_id] {result.session_id}")
        if result.blocked:
            print(f"❌ Bloqueado: {result.block_reason}")
        else:
            print(result.answer)
        return

    if args.command == "bg":
        if args.bg_command == "start":
            print(json.dumps(bg.start(args.prompt), indent=2, ensure_ascii=False))
        elif args.bg_command == "ps":
            print(json.dumps(bg.list(), indent=2, ensure_ascii=False))
        elif args.bg_command == "logs":
            print(bg.logs(args.job_id))
        elif args.bg_command == "kill":
            print(bg.kill(args.job_id))
        return

    if args.command == "memory":
        if args.memory_command == "put":
            runtime.memory.put(args.scope, args.key, args.value)
            print("ok")
        elif args.memory_command == "list":
            print(json.dumps(runtime.memory.list_scope(args.scope), indent=2, ensure_ascii=False))
        return

    if args.command == "vsearch":
        results = runtime.vector.search(args.query, top_k=args.top_k)
        if not results:
            print("Sin resultados semánticos.")
        for r in results:
            print(f"[{r.score:.3f}] {r.entry.key}: {r.entry.text[:200]}")
        return

    if args.command == "trace":
        if args.trace_command == "recent":
            spans = runtime.tracer.recent(20)
            print(json.dumps(spans, indent=2, ensure_ascii=False))
        elif args.trace_command == "session":
            spans = runtime.tracer.for_session(args.session_id)
            print(json.dumps(spans, indent=2, ensure_ascii=False))
        return

    if args.command == "cron":
        if args.cron_command == "add":
            print(json.dumps(scheduler_store.add(args.name, args.every_seconds, args.prompt), indent=2, ensure_ascii=False))
        elif args.cron_command == "list":
            print(json.dumps(scheduler_store.list(), indent=2, ensure_ascii=False))
        elif args.cron_command == "delete":
            print("deleted" if scheduler_store.delete(args.name) else "not-found")
        elif args.cron_command == "run-once":
            for msg in scheduler_engine.run_once():
                print(msg)
        elif args.cron_command == "run-loop":
            scheduler_engine.run_loop(sleep_seconds=args.sleep_seconds)
        return
