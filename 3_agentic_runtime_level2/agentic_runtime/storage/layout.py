from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from agentic_runtime.config import Settings


@dataclass(slots=True)
class RuntimeLayout:
    root: Path
    sessions: Path
    memory: Path
    jobs: Path
    logs: Path
    scheduler: Path
    workspaces: Path


    @classmethod
    def from_settings(cls, settings: Settings) -> 'RuntimeLayout':
        root = settings.data_dir
        layout = cls(
            root=root,
            sessions=root / 'sessions',
            memory=root / 'memory',
            jobs=root / 'jobs',
            logs=root / 'logs',
            scheduler=root / 'scheduler',
            workspaces=root / 'workspaces',
        )
        for item in layout.__dict__.values():
            if isinstance(item, Path):
                item.mkdir(parents=True, exist_ok=True)
        return layout
