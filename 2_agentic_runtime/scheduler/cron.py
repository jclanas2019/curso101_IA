import time
import threading

class CronScheduler:
    def __init__(self):
        self.jobs = []

    def add_job(self, interval, func):
        def loop():
            while True:
                time.sleep(interval)
                func()
        t = threading.Thread(target=loop, daemon=True)
        t.start()
        self.jobs.append(t)
