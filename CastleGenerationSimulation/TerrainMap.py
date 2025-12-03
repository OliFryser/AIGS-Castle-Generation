import numpy as np


class TerrainMap:
    def __init__(self, levelFilepath: str):
        with open(levelFilepath, "r") as f:
            self.width, self.height, self.maxHeight = [
                int(x) for x in f.readline().rstrip().split()
            ]
            self.map = np.zeros((self.height, self.width))
            for y in range(self.height):
                line = [float(num) for num in f.readline().rstrip().split()]
                for x in range(self.width):
                    self.map[y][x] = line[x]

            self.waterMap: set[tuple[int, int]] = set()
            self.path: set[tuple[int, int]] = set()

            self.target = None

            line = f.readline()
            parsedLine = [int(x) for x in line.rstrip().split()]
            if line == "":
                return

            if len(parsedLine) == 2:
                self.target = parsedLine[0], parsedLine[1]
                line = f.readline()
                parsedLine = [int(x) for x in line.rstrip().split()]

            if len(parsedLine) == 1:
                for i in range(int(line)):
                    x, y = map(int, f.readline().rstrip().split())
                    self.addWater(x, y)

            pathCount = f.readline()
            if pathCount == "":
                return

            for i in range(int(pathCount)):
                x, y = map(int, f.readline().rstrip().split())
                self.addPath(x, y)

    def getHeight(self, x: int, y: int) -> float:
        return self.map[y][x]

    def isWater(self, x, y) -> bool:
        return (x, y) in self.waterMap

    def addWater(self, x, y):
        self.waterMap.add((x, y))

    def removeWater(self, x, y):
        self.waterMap.discard((x, y))

    def isPath(self, x, y) -> bool:
        return (x, y) in self.path

    def addPath(self, x, y):
        self.path.add((x, y))

    def removePath(self, x, y):
        self.path.discard((x, y))

    def increaseHeight(self, x, y, amount):
        newHeight = self.map[y][x] + amount
        self.map[y][x] = min(newHeight, self.maxHeight)

    def decreaseHeight(self, x, y, amount):
        newHeight = self.map[y][x] - amount
        self.map[y][x] = max(newHeight, 0)

    def saveToFile(self, filepath: str):
        with open(filepath, "w") as f:
            # Write terrain
            line = f"{self.width} {self.height} {self.maxHeight}"
            f.write(line + "\n")

            for y in range(self.height):
                line = " ".join(str(self.getHeight(x, y)) for x in range(self.width))
                f.write(line + "\n")

            # Write target
            if self.target is not None:
                line = f"{self.target[0]} {self.target[1]}"
                f.write(line + "\n")

            # Write water
            line = f"{len(self.waterMap)}"
            f.write(line + "\n")

            for x, y in self.waterMap:
                f.write(f"{x} {y}\n")

            # Write path
            line = f"{len(self.path)}"
            f.write(line + "\n")

            for x, y in self.path:
                f.write(f"{x} {y}\n")

            print(f"Successfully saved terrain to {filepath}")
