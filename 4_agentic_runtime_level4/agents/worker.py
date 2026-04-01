
from isolation.container import Container

class Worker:
    def __init__(self, bus, tracer, memory):
        self.bus = bus
        self.tracer = tracer
        self.memory = memory
        self.container = Container()

    def run(self, task):
        self.tracer.log("worker_start", task)
        output = self.container.exec(task)
        self.tracer.log("worker_end", output)
        return output
