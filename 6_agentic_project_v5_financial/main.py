
from core.registry import Registry
from core.orchestrator import Orchestrator
from core.planner import Planner
from core.memory import Memory
from core.tracing import Tracer
from core.alerts import AlertEngine

from agents.retrieval import RetrievalAgent
from agents.financial import FinancialAgent
from agents.answer import AnswerAgent

def main():
    registry = Registry()
    memory = Memory("memory.json")
    tracer = Tracer()
    planner = Planner()
    alerts = AlertEngine()

    registry.register("retrieval", RetrievalAgent())
    registry.register("financial", FinancialAgent())
    registry.register("answer", AnswerAgent())

    orch = Orchestrator(registry, planner, memory, tracer, alerts)

    print("V5 Financial Agent (exit to quit)")
    while True:
        q = input("\nConsulta: ")
        if q.lower() in ["exit","salir"]:
            break

        result, triggered = orch.run(q)

        print("\n=== RESPUESTA ===")
        print(result)

        if triggered:
            print("\n=== ALERTAS ===")
            for a in triggered:
                print("-", a)

        print("\n=== TRACE ===")
        tracer.print()

if __name__ == "__main__":
    main()
