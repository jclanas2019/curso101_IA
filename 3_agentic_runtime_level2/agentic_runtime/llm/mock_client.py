from __future__ import annotations

from agentic_runtime.llm.base import LLMClient, LLMRequest


class MockLLMClient(LLMClient):
    def generate(self, request: LLMRequest) -> str:
        prompt = request.user_prompt.lower()
        if 'plan' in prompt:
            return 'Plan sugerido:
1. Entender objetivo
2. Revisar archivos
3. Ejecutar tools
4. Responder con evidencia local'
        if 'estado' in prompt or 'status' in prompt:
            return 'Estado: runtime operativo en modo mock. Puedes usar tools y memoria persistente.'
        return f'MOCK_RESPONSE: procesé la instrucción: {request.user_prompt}'
