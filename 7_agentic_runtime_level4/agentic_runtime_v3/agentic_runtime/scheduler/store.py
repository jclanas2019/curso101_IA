from __future__ import annotations

from pathlib import Path
from agentic_runtime.utils.io import read_json, write_json
from agentic_runtime.utils.time_utils import utc_now_iso


class SchedulerStore:
    def __init__(self, root: Path):
        self.path = root / 'jobs.json'

    def list(self) -> list[dict]:
        return read_json(self.path, default=[])

    def save(self, jobs: list[dict]) -> None:
        write_json(self.path, jobs)

    def add(self, name: str, every_seconds: int, prompt: str) -> dict:
        jobs = self.list()
        job = {
            'name': name,
            'every_seconds': every_seconds,
            'prompt': prompt,
            'last_run_at': None,
            'created_at': utc_now_iso(),
        }
        jobs = [j for j in jobs if j['name'] != name] + [job]
        self.save(jobs)
        return job

    def delete(self, name: str) -> bool:
        jobs = self.list()
        new_jobs = [j for j in jobs if j['name'] != name]
        self.save(new_jobs)
        return len(new_jobs) != len(jobs)
