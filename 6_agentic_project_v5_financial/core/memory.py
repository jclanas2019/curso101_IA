
import json, os
class Memory:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            with open(path,"w") as f: json.dump([],f)
    def add(self, role, content):
        d=self._read(); d.append({"role":role,"content":content}); self._write(d)
    def _read(self): return json.load(open(self.path))
    def _write(self,d): json.dump(d,open(self.path,"w"),indent=2)
