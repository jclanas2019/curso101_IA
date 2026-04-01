
from core.registry import Registry
from core.orchestrator import Orchestrator
from core.planner import Planner
from core.memory import Memory
from core.tracing import Tracer

from agents.retrieval import RetrievalAgent
from agents.energy import EnergyAgent
from agents.answer import AnswerAgent

def main():
    registry = Registry()
    memory = Memory("memory.json")
    tracer = Tracer()
    planner = Planner()

    registry.register("retrieval", RetrievalAgent())
    registry.register("energy", EnergyAgent())
    registry.register("answer", AnswerAgent())

    orch = Orchestrator(registry, planner, memory, tracer)

    print("V4 Agentic System (exit to quit)")
    while True:
        q = input("\nPregunta: ")
        if q.lower() in ["exit","salir"]:
            break

        result = orch.run(q)

        print("\n=== RESPUESTA ===")
        print(result)

        print("\n=== TRACE ===")
        tracer.print()

if __name__ == "__main__":
    main()
