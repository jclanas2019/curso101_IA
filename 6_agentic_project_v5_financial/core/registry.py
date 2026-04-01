class Registry:
 def __init__(self): self.agents={}
 def register(self,n,a): self.agents[n]=a
 def get(self,n): return self.agents.get(n)