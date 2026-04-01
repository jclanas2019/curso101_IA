from __future__ import annotations

from pathlib import Path
from typing import Any
from agentic_runtime.utils.io import read_json, write_json
from agentic_runtime.utils.time_utils import utc_now_iso


class JobStore:
    def __init__(self, jobs_dir: Path):
        self.jobs_dir = jobs_dir

    def _path(self, job_id: str) -> Path:
        return self.jobs_dir / f'{job_id}.json'

    def create(self, job_id: str, prompt: str, pid: int | None = None) -> dict[str, Any]:
        payload = {
            'job_id': job_id,
            'prompt': prompt,
            'pid': pid,
            'status': 'starting',
            'created_at': utc_now_iso(),
            'updated_at': utc_now_iso(),
        }
        write_json(self._path(job_id), payload)
        return payload

    def update(self, job_id: str, **fields: Any) -> dict[str, Any]:
        payload = read_json(self._path(job_id), default={})
        payload.update(fields)
        payload['updated_at'] = utc_now_iso()
        write_json(self._path(job_id), payload)
        return payload

    def get(self, job_id: str) -> dict[str, Any]:
        return read_json(self._path(job_id), default={})

    def list(self) -> list[dict[str, Any]]:
        result = []
        for path in sorted(self.jobs_dir.glob('*.json')):
            result.append(read_json(path, default={}))
        return result
