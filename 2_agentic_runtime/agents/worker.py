class WorkerAgent:
    def __init__(self, tools, memory):
        self.tools = tools
        self.memory = memory

    def execute(self, task: str):
        if "file" in task:
            return self.tools.run("file_read", task)
        elif "bash" in task:
            return self.tools.run("bash", task)
        else:
            return f"Processed task: {task}"
