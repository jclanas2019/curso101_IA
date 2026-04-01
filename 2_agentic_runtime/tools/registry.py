from tools.bash import BashTool
from tools.file_tool import FileTool

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "bash": BashTool(),
            "file_read": FileTool()
        }

    def run(self, name, input):
        if name in self.tools:
            return self.tools[name].run(input)
        return "Tool not found"
