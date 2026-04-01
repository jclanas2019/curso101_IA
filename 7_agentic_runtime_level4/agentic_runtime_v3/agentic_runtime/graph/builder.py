from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from agentic_runtime.agents.coordinator import Coordinator
from agentic_runtime.graph.nodes import (
    assembler_node,
    make_coder_node,
    make_llm_node,
    make_planner_node,
    make_vector_node,
)
from agentic_runtime.graph.state import AgentState
from agentic_runtime.infra.tracing import Tracer
from agentic_runtime.llm.base import LLMClient
from agentic_runtime.memory.vector_db import VectorDB


def build_graph(
    coordinator: Coordinator,
    llm: LLMClient,
    tracer: Tracer,
    vector_db: VectorDB,
):
    """Compila el grafo LangGraph del runtime.

    Flujo:
        START
          │
          ▼
      vector_node   ← recupera contexto semántico (VectorDB)
          │
          ▼
       planner      ← busca contexto en archivos (SearchTool) + tracing
          │
          ▼
        coder        ← opera sobre archivos / shell + tracing
          │
          ▼
      llm_node       ← genera respuesta con el modelo + tracing
          │
          ▼
      assembler      ← combina respuesta LLM + orquestación
          │
          ▼
         END
    """
    graph = StateGraph(AgentState)

    graph.add_node("vector_node", make_vector_node(vector_db, tracer))
    graph.add_node("planner",     make_planner_node(coordinator, tracer))
    graph.add_node("coder",       make_coder_node(coordinator, tracer))
    graph.add_node("llm_node",    make_llm_node(llm, tracer))
    graph.add_node("assembler",   assembler_node)

    graph.add_edge(START,         "vector_node")
    graph.add_edge("vector_node", "planner")
    graph.add_edge("planner",     "coder")
    graph.add_edge("coder",       "llm_node")
    graph.add_edge("llm_node",    "assembler")
    graph.add_edge("assembler",   END)

    return graph.compile()
