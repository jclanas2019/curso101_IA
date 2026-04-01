
from queue import Queue

class EventBus:
    def __init__(self):
        self.q = Queue()

    def publish(self, msg):
        self.q.put(msg)

    def consume(self):
        if not self.q.empty():
            return self.q.get()
