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
    print('Modo interactivo. Escribe exit para salir.')
    while True:
        user_input = input('>> ').strip()
        if user_input.lower() in {'exit', 'quit'}:
            break
        result = engine.run(user_input, session_id=session_id)
        session_id = result.session_id
        print(f'[session_id] {result.session_id}')
        print(result.answer)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='agentic-runtime')
    sub = parser.add_subparsers(dest='command', required=True)

    run_cmd = sub.add_parser('run')
    run_cmd.add_argument('prompt')
    run_cmd.add_argument('--session-id', default=None)

    sub.add_parser('interactive')

    bg = sub.add_parser('bg')
    bg_sub = bg.add_subparsers(dest='bg_command', required=True)
    bg_start = bg_sub.add_parser('start')
    bg_start.add_argument('prompt')
    bg_sub.add_parser('ps')
    bg_logs = bg_sub.add_parser('logs')
    bg_logs.add_argument('job_id')
    bg_kill = bg_sub.add_parser('kill')
    bg_kill.add_argument('job_id')

    mem = sub.add_parser('memory')
    mem_sub = mem.add_subparsers(dest='memory_command', required=True)
    mem_put = mem_sub.add_parser('put')
    mem_put.add_argument('scope', choices=['user', 'project', 'local'])
    mem_put.add_argument('key')
    mem_put.add_argument('value')
    mem_list = mem_sub.add_parser('list')
    mem_list.add_argument('scope', choices=['user', 'project', 'local'])

    cron = sub.add_parser('cron')
    cron_sub = cron.add_subparsers(dest='cron_command', required=True)
    cron_add = cron_sub.add_parser('add')
    cron_add.add_argument('name')
    cron_add.add_argument('every_seconds', type=int)
    cron_add.add_argument('prompt')
    cron_sub.add_parser('list')
    cron_del = cron_sub.add_parser('delete')
    cron_del.add_argument('name')
    cron_sub.add_parser('run-once')
    cron_loop = cron_sub.add_parser('run-loop')
    cron_loop.add_argument('--sleep-seconds', type=int, default=5)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    runtime = build_runtime()
    engine = QueryEngine(runtime)
    bg = BackgroundManager(runtime)
    scheduler_store = SchedulerStore(runtime.layout.scheduler)
    scheduler_engine = SchedulerEngine(runtime)

    if args.command == 'interactive':
        interactive(engine)
        return

    if args.command == 'run':
        result = engine.run(args.prompt, session_id=args.session_id)
        print(f'[session_id] {result.session_id}')
        print(result.answer)
        return

    if args.command == 'bg':
        if args.bg_command == 'start':
            print(json.dumps(bg.start(args.prompt), indent=2, ensure_ascii=False))
        elif args.bg_command == 'ps':
            print(json.dumps(bg.list(), indent=2, ensure_ascii=False))
        elif args.bg_command == 'logs':
            print(bg.logs(args.job_id))
        elif args.bg_command == 'kill':
            print(bg.kill(args.job_id))
        return

    if args.command == 'memory':
        if args.memory_command == 'put':
            runtime.memory.put(args.scope, args.key, args.value)
            print('ok')
        elif args.memory_command == 'list':
            print(json.dumps(runtime.memory.list_scope(args.scope), indent=2, ensure_ascii=False))
        return

    if args.command == 'cron':
        if args.cron_command == 'add':
            print(json.dumps(scheduler_store.add(args.name, args.every_seconds, args.prompt), indent=2, ensure_ascii=False))
        elif args.cron_command == 'list':
            print(json.dumps(scheduler_store.list(), indent=2, ensure_ascii=False))
        elif args.cron_command == 'delete':
            print('deleted' if scheduler_store.delete(args.name) else 'not-found')
        elif args.cron_command == 'run-once':
            for msg in scheduler_engine.run_once():
                print(msg)
        elif args.cron_command == 'run-loop':
            scheduler_engine.run_loop(sleep_seconds=args.sleep_seconds)
        return
