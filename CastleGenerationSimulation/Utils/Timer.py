import time

printTimer: bool = True


class Timer:
    def __init__(self, name: str, forcePrint = False):
        self.name = name
        self.forcePrint = forcePrint

    def start(self):
        if not printTimer and not self.forcePrint:
            return
        print(f"Started timer for {self.name}")
        self.startTime = time.time()

    def stop(self):
        if not printTimer and not self.forcePrint:
            return
        elapsedTime = time.time() - self.startTime
        print(f"Stopped timer for {self.name} - Took {elapsedTime:.3f} s")
