from __future__ import annotations

from openai import OpenAI
from agentic_runtime.llm.base import LLMClient, LLMRequest


class OpenAILLMClient(LLMClient):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, request: LLMRequest) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {'role': 'system', 'content': request.system_prompt},
                {'role': 'user', 'content': request.user_prompt},
            ],
        )
        return response.output_text
