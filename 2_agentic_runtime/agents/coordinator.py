from agents.worker import WorkerAgent

class Coordinator:
    def __init__(self, tools, memory):
        self.tools = tools
        self.memory = memory

    def handle(self, task: str):
        worker = WorkerAgent(self.tools, self.memory)
        return worker.execute(task)
