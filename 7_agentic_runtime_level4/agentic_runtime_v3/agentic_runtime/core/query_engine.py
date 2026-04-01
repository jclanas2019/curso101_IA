from __future__ import annotations

import uuid
from dataclasses import dataclass

from agentic_runtime.agents.coordinator import Coordinator
from agentic_runtime.core.runtime import RuntimeContainer
from agentic_runtime.graph.builder import build_graph
from agentic_runtime.infra.queue import Event
from agentic_runtime.llm.mock_client import MockLLMClient
from agentic_runtime.llm.openai_client import OpenAILLMClient
from agentic_runtime.memory.prompt_builder import MemoryPromptBuilder


@dataclass(slots=True)
class QueryResult:
    session_id: str
    answer: str
    blocked: bool = False
    block_reason: str = ""


class QueryEngine:
    """Motor de consultas que orquesta el flujo de agentes via LangGraph.

    Integración Level 4:
    - PolicyEngine  → verifica el prompt antes de ejecutar el grafo
    - EventBus      → publica eventos user.input / agent.response
    - Tracer        → mide duración de cada nodo del grafo
    - VectorDB      → enriquece el system_prompt con contexto semántico

    Modelo configurado en .env:
        OPENAI_MODEL=gpt-4.1-mini
        AGENTIC_DEFAULT_MODE=openai | mock
    """

    def __init__(self, runtime: RuntimeContainer):
        self.runtime = runtime
        self.memory_prompt_builder = MemoryPromptBuilder(runtime.memory)
        self.coordinator = Coordinator(
            runtime.tools, runtime.memory, runtime.layout.workspaces
        )

        # Conectar VectorDB al MemoryStore para indexado automático
        runtime.memory.attach_vector_db(runtime.vector)

        # Seleccionar cliente LLM
        if runtime.settings.default_mode == "openai" and runtime.settings.openai_api_key:
            self.llm = OpenAILLMClient(
                runtime.settings.openai_api_key,
                runtime.settings.openai_model,
            )
        else:
            self.llm = MockLLMClient()

        # Compilar el grafo LangGraph (incluye vector_node y tracing)
        self._graph = build_graph(
            coordinator=self.coordinator,
            llm=self.llm,
            tracer=runtime.tracer,
            vector_db=runtime.vector,
        )

    def _system_prompt(self) -> str:
        memory_context = self.memory_prompt_builder.build()
        tools_help = self.runtime.tools.help()
        return (
            "Eres un runtime agentico local con memoria y tools. "
            "Antes de responder, privilegia evidencia local. "
            "Tools disponibles:\n" + tools_help + "\n\n" + memory_context
        ).strip()

    def _ensure_session(self, session_id: str | None) -> str:
        sid = session_id or str(uuid.uuid4())
        self.runtime.sessions.create_if_missing(sid)
        return sid

    def run(self, user_input: str, session_id: str | None = None) -> QueryResult:
        sid = self._ensure_session(session_id)

        # --- PolicyEngine: bloquear si viola reglas ---
        policy_result = self.runtime.policy.check_task(user_input)
        if not policy_result:
            reason = policy_result.violation.reason if policy_result.violation else "política"
            self.runtime.tracer.log("policy_block", reason, session_id=sid)
            return QueryResult(session_id=sid, answer=f"❌ Bloqueado: {reason}", blocked=True, block_reason=reason)

        # --- EventBus: publicar evento de entrada ---
        self.runtime.bus.publish(
            Event(topic="user.input", payload=user_input, source=sid)
        )

        self.runtime.sessions.append_message(sid, "user", user_input)
        self.runtime.tracer.log("query_start", user_input, node="query_engine", session_id=sid)

        # --- Ejecutar grafo LangGraph ---
        initial_state = {
            "user_input": user_input,
            "session_id": sid,
            "system_prompt": self._system_prompt(),
            "vector_context": "",
            "plan_result": "",
            "code_result": "",
            "llm_answer": "",
            "final_answer": "",
            "trace_spans": [],
            "error": "",
        }

        with self.runtime.tracer.span("graph_invoke", node="query_engine", session_id=sid):
            output_state = self._graph.invoke(initial_state)

        final_answer = output_state.get("final_answer", "")

        # --- EventBus: publicar respuesta + despachar suscriptores ---
        self.runtime.bus.publish(
            Event(topic="agent.response", payload=final_answer[:500], source=sid)
        )
        self.runtime.bus.dispatch_all()

        # --- Persistir en sesión, memoria y VectorDB (via MemoryStore) ---
        self.runtime.sessions.append_message(sid, "assistant", final_answer)
        self.runtime.memory.put("project", "last_user_request", user_input)
        self.runtime.memory.put("project", "last_assistant_answer", final_answer[:2000])

        self.runtime.tracer.log("query_end", f"{len(final_answer)} chars", node="query_engine", session_id=sid)

        return QueryResult(session_id=sid, answer=final_answer)
