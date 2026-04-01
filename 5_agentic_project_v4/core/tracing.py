
class Tracer:
    def __init__(self):
        self.steps = []
    def log(self, step, data):
        self.steps.append((step, data))
    def print(self):
        for s,d in self.steps:
            print(f"[{s}] -> {d}")
        self.steps = []
