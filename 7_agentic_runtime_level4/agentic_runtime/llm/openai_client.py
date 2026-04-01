from __future__ import annotations

from openai import OpenAI
from agentic_runtime.llm.base import LLMClient, LLMRequest


class OpenAILLMClient(LLMClient):
    """Cliente LLM sobre OpenAI Chat Completions API.

    Usa `chat.completions.create` para máxima compatibilidad con
    todos los modelos, incluyendo gpt-4.1-mini.
    El modelo y la API key se cargan desde las Settings (vía .env).
    """

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, request: LLMRequest) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
