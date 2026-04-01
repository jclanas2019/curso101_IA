from __future__ import annotations

import time
from datetime import datetime, timezone
from agentic_runtime.core.background_manager import BackgroundManager
from agentic_runtime.core.runtime import RuntimeContainer
from agentic_runtime.scheduler.store import SchedulerStore
from agentic_runtime.utils.time_utils import utc_now_iso


class SchedulerEngine:
    def __init__(self, runtime: RuntimeContainer):
        self.runtime = runtime
        self.store = SchedulerStore(runtime.layout.scheduler)
        self.bg = BackgroundManager(runtime)

    def run_once(self) -> list[str]:
        messages: list[str] = []
        now = datetime.now(timezone.utc)
        jobs = self.store.list()
        changed = False
        for job in jobs:
            last = job.get('last_run_at')
            should_run = False
            if last is None:
                should_run = True
            else:
                last_dt = datetime.fromisoformat(last)
                elapsed = (now - last_dt).total_seconds()
                should_run = elapsed >= job['every_seconds']
            if should_run:
                payload = self.bg.start(job['prompt'])
                job['last_run_at'] = utc_now_iso()
                messages.append(f"{job['name']} -> launched {payload['job_id']}")
                changed = True
        if changed:
            self.store.save(jobs)
        return messages

    def run_loop(self, sleep_seconds: int = 5) -> None:
        print('Scheduler loop iniciado. Ctrl+C para salir.')
        while True:
            messages = self.run_once()
            for item in messages:
                print(item)
            time.sleep(sleep_seconds)
