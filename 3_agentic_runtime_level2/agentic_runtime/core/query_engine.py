from __future__ import annotations

import uuid
from dataclasses import dataclass
from agentic_runtime.agents.coordinator import Coordinator
from agentic_runtime.core.runtime import RuntimeContainer
from agentic_runtime.llm.base import LLMRequest
from agentic_runtime.llm.mock_client import MockLLMClient
from agentic_runtime.llm.openai_client import OpenAILLMClient
from agentic_runtime.memory.prompt_builder import MemoryPromptBuilder


@dataclass(slots=True)
class QueryResult:
    session_id: str
    answer: str


class QueryEngine:
    def __init__(self, runtime: RuntimeContainer):
        self.runtime = runtime
        self.memory_prompt_builder = MemoryPromptBuilder(runtime.memory)
        self.coordinator = Coordinator(runtime.tools, runtime.memory, runtime.layout.workspaces)
        if runtime.settings.default_mode == 'openai' and runtime.settings.openai_api_key:
            self.llm = OpenAILLMClient(runtime.settings.openai_api_key, runtime.settings.openai_model)
        else:
            self.llm = MockLLMClient()

    def _system_prompt(self) -> str:
        memory_context = self.memory_prompt_builder.build()
        tools_help = self.runtime.tools.help()
        return (
            'Eres un runtime agentico local con memoria y tools. '            'Antes de responder, privilegia evidencia local. '            'Tools disponibles:
' + tools_help + '

' + memory_context
        ).strip()

    def _ensure_session(self, session_id: str | None) -> str:
        sid = session_id or str(uuid.uuid4())
        self.runtime.sessions.create_if_missing(sid)
        return sid

    def run(self, user_input: str, session_id: str | None = None) -> QueryResult:
        sid = self._ensure_session(session_id)
        self.runtime.sessions.append_message(sid, 'user', user_input)

        orchestration = self.coordinator.handle(user_input, sid)
        llm_answer = self.llm.generate(LLMRequest(system_prompt=self._system_prompt(), user_prompt=user_input))
        final_answer = f'{llm_answer}

[orchestration]
{orchestration}'

        self.runtime.sessions.append_message(sid, 'assistant', final_answer)
        self.runtime.memory.put('project', 'last_user_request', user_input)
        self.runtime.memory.put('project', 'last_assistant_answer', final_answer[:2000])
        return QueryResult(session_id=sid, answer=final_answer)
