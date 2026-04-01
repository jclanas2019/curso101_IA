from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    """Estado compartido que fluye por todos los nodos del grafo."""
    user_input: str
    session_id: str
    system_prompt: str
    vector_context: str    # contexto semántico recuperado por VectorDB
    plan_result: str       # resultado del nodo planner
    code_result: str       # resultado del nodo coder
    llm_answer: str        # respuesta del LLM
    final_answer: str      # respuesta ensamblada final
    trace_spans: list      # spans emitidos durante este run
    error: str
