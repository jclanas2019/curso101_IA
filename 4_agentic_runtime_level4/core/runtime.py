
from core.orchestrator import Orchestrator
from infra.queue import EventBus
from infra.tracing import Tracer
from infra.policy import PolicyEngine
from memory.vector_db import VectorDB

class Runtime:
    def __init__(self):
        self.bus = EventBus()
        self.tracer = Tracer()
        self.policy = PolicyEngine()
        self.memory = VectorDB()
        self.orchestrator = Orchestrator(self.bus, self.tracer, self.memory)

    def start(self):
        while True:
            task = input(">> ")
            if task in ["exit","quit"]:
                break

            self.tracer.log("input", task)

            if not self.policy.allow(task):
                print("❌ blocked by policy")
                continue

            self.bus.publish(task)
            result = self.orchestrator.process(task)

            self.memory.store(task, result)
            print(result)
