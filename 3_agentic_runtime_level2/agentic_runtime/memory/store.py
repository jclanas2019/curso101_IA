from __future__ import annotations

from pathlib import Path
from typing import Any
from agentic_runtime.utils.io import read_json, write_json
from agentic_runtime.utils.time_utils import utc_now_iso

SCOPES = ('user', 'project', 'local')


class MemoryStore:
    def __init__(self, root: Path):
        self.root = root
        for scope in SCOPES:
            (self.root / scope).mkdir(parents=True, exist_ok=True)

    def _path(self, scope: str, key: str) -> Path:
        if scope not in SCOPES:
            raise ValueError(f'Invalid memory scope: {scope}')
        safe_key = key.replace('/', '_')
        return self.root / scope / f'{safe_key}.json'

    def put(self, scope: str, key: str, value: Any) -> None:
        payload = {
            'key': key,
            'scope': scope,
            'updated_at': utc_now_iso(),
            'value': value,
        }
        write_json(self._path(scope, key), payload)

    def get(self, scope: str, key: str, default: Any = None) -> Any:
        payload = read_json(self._path(scope, key), default=None)
        if payload is None:
            return default
        return payload.get('value', default)

    def list_scope(self, scope: str) -> list[dict[str, Any]]:
        out = []
        for path in sorted((self.root / scope).glob('*.json')):
            out.append(read_json(path, default={}))
        return out
