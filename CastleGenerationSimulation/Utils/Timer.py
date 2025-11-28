import time

printTimer: bool = True


class Timer:
    def __init__(self, name: str):
        self.name = name

    def start(self):
        if not printTimer:
            return
        print(f"Started timer for {self.name}")
        self.startTime = time.time()

    def stop(self):
        if not printTimer:
            return
        elapsedTime = time.time() - self.startTime
        print(f"Stopped timer for {self.name} - Took {elapsedTime:.3f} s")
