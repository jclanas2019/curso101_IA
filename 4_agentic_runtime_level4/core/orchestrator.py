
from agents.coordinator import Coordinator

class Orchestrator:
    def __init__(self, bus, tracer, memory):
        self.coordinator = Coordinator(bus, tracer, memory)

    def process(self, task):
        return self.coordinator.execute(task)
