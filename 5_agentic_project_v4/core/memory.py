
import json, os
class Memory:
    def __init__(self, path):
        self.path = path
        if not os.path.exists(path):
            with open(path,"w") as f: json.dump([],f)

    def add(self, role, content):
        data = self._read()
        data.append({"role":role,"content":content})
        self._write(data)

    def _read(self):
        with open(self.path) as f: return json.load(f)

    def _write(self, data):
        with open(self.path,"w") as f: json.dump(data,f,indent=2)
