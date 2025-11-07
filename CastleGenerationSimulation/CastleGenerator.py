from enum import IntEnum
from CastleElement import CastleElement, ElementType
import numpy as np


class Direction(IntEnum):
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3


class CastleGenerationAgent:
    def __init__(
        self,
        cursor: tuple[int, int],
        initialDirection: Direction,
        instructions: str,
        grid: list[list[None | CastleElement]],
    ):
        self.directionToOffset = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }

        self.cursor = cursor
        self.grid = grid
        self.instructions = instructions.split()
        # reverse to be able to pop in constant time. Converting from a stack to a queue
        self.instructions.reverse()
        self.direction = initialDirection

    def getNextInstruction(self) -> str | None:
        if len(self.instructions) <= 0:
            return None
        return self.instructions.pop()

    def placeNextElement(self, tile, elemap):
        self.moveCursorInDirection(len(tile[0]))
        if self.direction == Direction.UP or self.direction == Direction.DOWN:
            tile = np.transpose(tile)
        for n in range(len(tile)):
            for i in range(len(tile[n])):
                    
                t  = tile[n][i]
                if t in elemap:
                    self.grid[self.cursor[1]+ n][self.cursor[0] + i] = CastleElement(elemap[t])

    def turnClockwise(self):
        # Add 1 modulo 4
        self.direction = Direction((self.direction + 1) % 4)

    def turnCounterClockwise(self):
        # Subtract 1 modulo 4
        self.direction = Direction((self.direction - 1) % 4)

    def moveCursorInDirection(self, range = 1):
        offset = self.directionToOffset[self.direction]
        self.cursor = (self.cursor[0] + offset[0] * range, self.cursor[1] + offset[1] * range)


class CastleGenerator:
    def __init__(self, filepath, tilePath, width: int, height: int):
        self.letterToElementType = {
            "K": ElementType.KEEP,
            "W": ElementType.WALL,
            "G": ElementType.GATE,
            "T": ElementType.TOWER,
        }
        self.tileMap = self.loadTileMap(tilePath)

        self.width = width #// 3
        self.height = height #// 3

        self.grid: list[list[None | CastleElement]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # Place keep in center
        self.center = (self.width // 2, self.height // 2)
        #self.grid[self.center[1]][self.center[0]] = CastleElement(ElementType.KEEP)

        self.generate(filepath)

    def loadTileMap(self, filepath: str):
        
        tileMap = {}
        for element in ElementType:
            with open(filepath + element.value + ".txt", "r") as f:
                tileMap[element] = [line.strip().split() for line in f]
            f.close()
        return tileMap

    def generate(self, filepath: str):
        with open(filepath, "r") as f:
            self.instructions = [line.strip() for line in f]
            self.instructions.reverse()

        agents: list[CastleGenerationAgent] = []
        agents.append(
            CastleGenerationAgent(
                self.center, Direction.UP, self.instructions.pop(), self.grid
            )
        )

        while len(agents) > 0:
            self.step(agents)

    def step(self, agents: list[CastleGenerationAgent]):
        for agent in agents:
            instruction = agent.getNextInstruction()
            if instruction is None:
                agents.remove(agent)
                continue

            if instruction == "LEFT":
                agent.turnCounterClockwise()
            elif instruction == "RIGHT":
                agent.turnClockwise()
            elif instruction == "BRANCH":
                agents.append(
                    CastleGenerationAgent(
                        agent.cursor,
                        agent.direction,
                        self.instructions.pop(),
                        self.grid,
                    )
                )
            else:
                elementType = self.letterToElementType[instruction]
                agent.placeNextElement(self.tileMap[elementType], self.letterToElementType)

    def getCastleMapInTerrainScale(self):
        scale = 1
        return [
            [cell for cell in row for _ in range(scale)]
            for row in self.grid
            for _ in range(scale)
        ]
