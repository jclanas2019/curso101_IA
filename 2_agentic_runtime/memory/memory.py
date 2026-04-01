class Memory:
    def __init__(self):
        self.data = []

    def store(self, role, content):
        self.data.append({"role": role, "content": content})

    def get_all(self):
        return self.data
