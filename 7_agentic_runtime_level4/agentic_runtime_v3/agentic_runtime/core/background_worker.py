from __future__ import annotations

import argparse
import os
import signal
import sys
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from agentic_runtime.core.query_engine import QueryEngine
from agentic_runtime.core.runtime import build_runtime


def run_job(prompt: str, log_path: str, session_id: str | None = None) -> int:
    runtime = build_runtime()
    engine = QueryEngine(runtime)
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as log_handle, redirect_stdout(log_handle), redirect_stderr(log_handle):
        print(f'[pid={os.getpid()}] starting job')
        print(f'[prompt] {prompt}')
        try:
            result = engine.run(prompt, session_id=session_id)
            print(f'[session_id] {result.session_id}')
            print(result.answer)
            print('[status] finished')
            return 0
        except Exception:
            traceback.print_exc()
            return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--log-path', required=True)
    parser.add_argument('--session-id', required=False)
    args = parser.parse_args()
    return run_job(args.prompt, args.log_path, args.session_id)


if __name__ == '__main__':
    raise SystemExit(main())
