
import subprocess

class Container:
    def exec(self, cmd):
        try:
            return subprocess.getoutput(cmd)
        except Exception as e:
            return str(e)
