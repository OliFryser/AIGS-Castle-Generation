import random


class RandomLevelGenerator:
    def __init__(self, maxHeight):
        self.maxHeight = maxHeight

    def getHeight(self, x, y):
        return random.randint(0, self.maxHeight)
