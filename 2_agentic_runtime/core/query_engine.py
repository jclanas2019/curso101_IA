from tools.registry import ToolRegistry
from agents.coordinator import Coordinator
from memory.memory import Memory

class QueryEngine:
    def __init__(self):
        self.memory = Memory()
        self.tools = ToolRegistry()
        self.coordinator = Coordinator(self.tools, self.memory)

    def run(self, user_input: str):
        self.memory.store("user", user_input)
        result = self.coordinator.handle(user_input)
        self.memory.store("assistant", result)
        return result
