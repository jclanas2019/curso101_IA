
import time

class Tracer:
    def log(self, event, data):
        print(f"[TRACE] {event} -> {data} @ {time.time()}")
