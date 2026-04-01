
class VectorDB:
    def __init__(self):
        self.store_db = []

    def store(self, inp, out):
        self.store_db.append((inp, out))

    def search(self, query):
        return [x for x in self.store_db if query in x[0]]
