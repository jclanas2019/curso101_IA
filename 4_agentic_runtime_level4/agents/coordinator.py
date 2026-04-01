
from agents.worker import Worker

class Coordinator:
    def __init__(self, bus, tracer, memory):
        self.bus = bus
        self.tracer = tracer
        self.memory = memory

    def execute(self, task):
        worker = Worker(self.bus, self.tracer, self.memory)
        return worker.run(task)
