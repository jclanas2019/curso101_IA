from __future__ import annotations

from pathlib import Path
from typing import Any
from agentic_runtime.utils.io import read_json, write_json
from agentic_runtime.utils.time_utils import utc_now_iso


class SessionStore:
    def __init__(self, sessions_dir: Path):
        self.sessions_dir = sessions_dir

    def path_for(self, session_id: str) -> Path:
        return self.sessions_dir / f'{session_id}.json'

    def create_if_missing(self, session_id: str) -> dict[str, Any]:
        path = self.path_for(session_id)
        data = read_json(path, default=None)
        if data is None:
            data = {
                'session_id': session_id,
                'created_at': utc_now_iso(),
                'updated_at': utc_now_iso(),
                'messages': [],
                'usage': {'turns': 0},
            }
            write_json(path, data)
        return data

    def append_message(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        data = self.create_if_missing(session_id)
        data['messages'].append({
            'ts': utc_now_iso(),
            'role': role,
            'content': content,
            'metadata': metadata or {},
        })
        data['usage']['turns'] += 1 if role == 'user' else 0
        data['updated_at'] = utc_now_iso()
        write_json(self.path_for(session_id), data)

    def load(self, session_id: str) -> dict[str, Any]:
        return self.create_if_missing(session_id)
