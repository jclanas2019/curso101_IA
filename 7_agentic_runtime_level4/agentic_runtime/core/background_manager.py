from __future__ import annotations

import os
import signal
import subprocess
import sys
import uuid
from pathlib import Path
from agentic_runtime.core.runtime import RuntimeContainer


class BackgroundManager:
    def __init__(self, runtime: RuntimeContainer):
        self.runtime = runtime

    def start(self, prompt: str) -> dict:
        job_id = str(uuid.uuid4())
        log_path = self.runtime.layout.logs / f'{job_id}.log'
        self.runtime.jobs.create(job_id, prompt)
        cmd = [
            sys.executable,
            '-m',
            'agentic_runtime.core.background_worker',
            '--prompt',
            prompt,
            '--log-path',
            str(log_path),
        ]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        payload = self.runtime.jobs.update(job_id, pid=proc.pid, status='running', log_path=str(log_path))
        return payload

    def list(self) -> list[dict]:
        rows = []
        for job in self.runtime.jobs.list():
            pid = job.get('pid')
            if pid and not self._pid_exists(pid) and job.get('status') == 'running':
                self.runtime.jobs.update(job['job_id'], status='finished')
                job = self.runtime.jobs.get(job['job_id'])
            rows.append(job)
        return rows

    def logs(self, job_id: str) -> str:
        job = self.runtime.jobs.get(job_id)
        log_path = job.get('log_path')
        if not log_path:
            return 'No hay log disponible'
        path = Path(log_path)
        if not path.exists():
            return 'El archivo de log aún no existe'
        return path.read_text(encoding='utf-8')

    def kill(self, job_id: str) -> str:
        job = self.runtime.jobs.get(job_id)
        pid = job.get('pid')
        if not pid:
            return 'Job sin PID'
        try:
            os.kill(pid, signal.SIGTERM)
            self.runtime.jobs.update(job_id, status='killed')
            return f'Job {job_id} terminado'
        except ProcessLookupError:
            self.runtime.jobs.update(job_id, status='finished')
            return f'Job {job_id} ya no estaba activo'

    @staticmethod
    def _pid_exists(pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
