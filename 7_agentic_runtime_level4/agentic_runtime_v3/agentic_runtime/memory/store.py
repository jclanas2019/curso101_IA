from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from agentic_runtime.utils.io import read_json, write_json
from agentic_runtime.utils.time_utils import utc_now_iso

if TYPE_CHECKING:
    from agentic_runtime.memory.vector_db import VectorDB

SCOPES = ("user", "project", "local")


class MemoryStore:
    """Almacén de memoria persistente por scope.

    Si se provee un VectorDB, cada valor almacenado se indexa
    automáticamente para permitir búsqueda semántica posterior.
    """

    def __init__(self, root: Path, vector_db: "VectorDB | None" = None) -> None:
        self.root = root
        self._vector_db = vector_db
        for scope in SCOPES:
            (self.root / scope).mkdir(parents=True, exist_ok=True)

    def attach_vector_db(self, vector_db: "VectorDB") -> None:
        """Conecta un VectorDB después de la construcción (evita ciclos)."""
        self._vector_db = vector_db

    def _path(self, scope: str, key: str) -> Path:
        if scope not in SCOPES:
            raise ValueError(f"Invalid memory scope: {scope}")
        safe_key = key.replace("/", "_")
        return self.root / scope / f"{safe_key}.json"

    def put(self, scope: str, key: str, value: Any) -> None:
        payload = {
            "key": key,
            "scope": scope,
            "updated_at": utc_now_iso(),
            "value": value,
        }
        write_json(self._path(scope, key), payload)

        # Indexar en VectorDB si está disponible
        if self._vector_db is not None and isinstance(value, str) and value.strip():
            self._vector_db.store(
                key=f"{scope}:{key}",
                text=value,
                metadata={"scope": scope, "key": key},
            )

    def get(self, scope: str, key: str, default: Any = None) -> Any:
        payload = read_json(self._path(scope, key), default=None)
        if payload is None:
            return default
        return payload.get("value", default)

    def list_scope(self, scope: str) -> list[dict[str, Any]]:
        out = []
        for path in sorted((self.root / scope).glob("*.json")):
            out.append(read_json(path, default={}))
        return out
