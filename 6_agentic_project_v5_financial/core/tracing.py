
class Tracer:
    def __init__(self): self.steps=[]
    def log(self,s,d): self.steps.append((s,d))
    def print(self):
        for s,d in self.steps: print(f"[{s}] -> {d}")
        self.steps=[]
