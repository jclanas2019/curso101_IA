from __future__ import annotations

from agentic_runtime.agents.coordinator import Coordinator
from agentic_runtime.graph.state import AgentState
from agentic_runtime.infra.tracing import Tracer
from agentic_runtime.llm.base import LLMClient, LLMRequest
from agentic_runtime.memory.vector_db import VectorDB


# ---------------------------------------------------------------------------
# Nodo 0: Vector Retriever
# Recupera contexto semántico del VectorDB antes de que actúen los agentes.
# ---------------------------------------------------------------------------

def make_vector_node(vector_db: VectorDB, tracer: Tracer):
    def vector_node(state: AgentState) -> AgentState:
        sid = state["session_id"]
        with tracer.span("vector_retrieve", node="vector_node", session_id=sid) as span:
            context = vector_db.search_as_context(state["user_input"], top_k=5)
            span.data = f"{vector_db.count()} entradas, {len(context)} chars recuperados"
        return {**state, "vector_context": context}
    return vector_node


# ---------------------------------------------------------------------------
# Nodo 1: Planner
# ---------------------------------------------------------------------------

def make_planner_node(coordinator: Coordinator, tracer: Tracer):
    def planner_node(state: AgentState) -> AgentState:
        sid = state["session_id"]
        with tracer.span("planner_execute", node="planner", session_id=sid) as span:
            try:
                planner = coordinator._planner()
                query = state["user_input"].replace("plan", "").strip() or "README"
                result = planner.execute(f"search {query}", sid)
                span.data = result.summary[:200]
                return {**state, "plan_result": result.summary}
            except Exception as exc:
                span.data = f"error: {exc}"
                return {**state, "plan_result": f"[planner error] {exc}"}
    return planner_node


# ---------------------------------------------------------------------------
# Nodo 2: Coder
# ---------------------------------------------------------------------------

def make_coder_node(coordinator: Coordinator, tracer: Tracer):
    def coder_node(state: AgentState) -> AgentState:
        sid = state["session_id"]
        with tracer.span("coder_execute", node="coder", session_id=sid) as span:
            try:
                coder = coordinator._coder()
                result = coder.execute(state["user_input"], sid)
                span.data = result.summary[:200]
                return {**state, "code_result": result.summary}
            except Exception as exc:
                span.data = f"error: {exc}"
                return {**state, "code_result": f"[coder error] {exc}"}
    return coder_node


# ---------------------------------------------------------------------------
# Nodo 3: LLM Response
# ---------------------------------------------------------------------------

def make_llm_node(llm: LLMClient, tracer: Tracer):
    def llm_node(state: AgentState) -> AgentState:
        sid = state["session_id"]
        # Enriquecer el system_prompt con contexto semántico si existe
        enriched_prompt = state["system_prompt"]
        if state.get("vector_context"):
            enriched_prompt = state["vector_context"] + "\n\n" + enriched_prompt

        with tracer.span("llm_generate", node="llm_node", session_id=sid) as span:
            try:
                answer = llm.generate(
                    LLMRequest(
                        system_prompt=enriched_prompt,
                        user_prompt=state["user_input"],
                    )
                )
                span.data = answer[:200]
                return {**state, "llm_answer": answer}
            except Exception as exc:
                span.data = f"error: {exc}"
                return {**state, "llm_answer": f"[llm error] {exc}"}
    return llm_node


# ---------------------------------------------------------------------------
# Nodo 4: Assembler
# ---------------------------------------------------------------------------

def assembler_node(state: AgentState) -> AgentState:
    parts: list[str] = []

    if state.get("llm_answer"):
        parts.append(state["llm_answer"])

    orchestration_parts: list[str] = []
    if state.get("plan_result"):
        orchestration_parts.append(f"[planner]\n{state['plan_result']}")
    if state.get("code_result"):
        orchestration_parts.append(f"[coder]\n{state['code_result']}")

    if orchestration_parts:
        parts.append("\n[orchestration]\n" + "\n".join(orchestration_parts))

    final = "\n".join(parts).strip()
    return {**state, "final_answer": final}
