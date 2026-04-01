from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(slots=True)
class Settings:
    data_dir: Path
    openai_api_key: str | None
    openai_model: str
    default_mode: str


def get_settings() -> Settings:
    data_dir = Path(os.getenv('AGENTIC_DATA_DIR', './runtime_data')).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    return Settings(
        data_dir=data_dir,
        openai_api_key=os.getenv('OPENAI_API_KEY') or None,
        openai_model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
        default_mode=os.getenv('AGENTIC_DEFAULT_MODE', 'mock').strip().lower(),
    )
