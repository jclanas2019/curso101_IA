import threading

class BackgroundRunner:
    def run(self, func, *args):
        t = threading.Thread(target=func, args=args)
        t.start()
        return "Task started in background"
