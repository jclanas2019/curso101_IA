import subprocess

class BashTool:
    def run(self, command: str):
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            return output
        except Exception as e:
            return str(e)
