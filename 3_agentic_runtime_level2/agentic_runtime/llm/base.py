from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str


class LLMClient(Protocol):
    def generate(self, request: LLMRequest) -> str:
        ...
