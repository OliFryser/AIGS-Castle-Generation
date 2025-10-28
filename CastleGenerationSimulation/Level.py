import numpy as np


class Level:
    def __init__(self, levelFilepath: str):
        self.createLevel(levelFilepath)

    def createLevel(self, levelFilepath: str):
        with open(levelFilepath, "r") as f:
            self.width, self.height, self.max_height = [
                int(x) for x in f.readline().rstrip().split()
            ]
            self.level = np.zeros((self.height, self.width))
            for y in range(self.height):
                line = [float(num) for num in f.readline().rstrip().split()]
                for x in range(self.width):
                    self.level[y][x] = line[x]

    def getLevel(self):
        return self.level

    def getCell(self, x, y):
        return float(self.level[y][x])

    def getNeighbors(self, x, y) -> list[tuple[int, int]]:
        return [
            (x, np.clip(y + 1, 0, self.height)),
            (np.clip(x + 1, 0, self.width), np.clip(y + 1, 0, self.height)),
            (np.clip(x + 1, 0, self.width), y),
            (np.clip(x + 1, 0, self.width), np.clip(y - 1, 0, self.height)),
            (x, np.clip(y - 1, 0, self.height)),
            (np.clip(x - 1, 0, self.width), np.clip(y - 1, 0, self.height)),
            (np.clip(x - 1, 0, self.width), y),
            (np.clip(x - 1, 0, self.width), np.clip(y + 1, 0, self.height)),
        ]

    def getImmediateNeighbors(self, x, y):
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        x1 = np.clip(x0 + 1, 0, self.width)
        y1 = np.clip(y0 + 1, 0, self.height)
        return [(x0, y0), (x1, y0), (x0, y1), (x1, y1)]

    def getBilinearHeight(self, x: float, y: float) -> float:
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        x1 = x0 + 1
        y1 = y0 + 1

        # edge guard
        max_y, max_x = self.height, self.width
        x0 = np.clip(x0, 0, max_x - 1)
        x1 = np.clip(x1, 0, max_x - 1)
        y0 = np.clip(y0, 0, max_y - 1)
        y1 = np.clip(y1, 0, max_y - 1)

        tx = x - x0
        ty = y - y0

        return (
            self.getCell(x0, y0) * (1 - tx) * (1 - ty)
            + self.getCell(x1, y0) * tx * (1 - ty)
            + self.getCell(x0, y1) * (1 - tx) * ty
            + self.getCell(x1, y1) * tx * ty
        )
