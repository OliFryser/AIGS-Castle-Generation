import time


class Timer:
    def __init__(self, name: str):
        self.name = name

    def start(self):
        print(f"Started timer for {self.name}")
        self.startTime = time.time()

    def stop(self):
        elapsedTime = time.time() - self.startTime
        print(f"Ended timer for {self.name} - Took {elapsedTime:.3f} s")
