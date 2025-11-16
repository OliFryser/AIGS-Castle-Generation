from enum import IntEnum
import numpy as np

from CastleElement import CastleElement, ElementType
from CastleInstructions.InstructionToken import InstructionToken
from CastleInstructions.InstructionTree import parseInstructionTree
from CastleInstructions.InstructionLine import InstructionLine


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
        instructionLine: InstructionLine,
        grid: list[list[None | CastleElement]],
    ):
        self.instructionLine = instructionLine

        self.directionToOffset = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }

        self.cursor = cursor
        self.grid = grid
        self.direction = initialDirection

    def getNextInstruction(self) -> InstructionToken | None:
        if self.instructionLine.isEmpty():
            return None
        return self.instructionLine.getNextInstruction()

    def placeNextElement(self, tile, elemap):
        self.moveCursorInDirection(len(tile[0]))
        if self.direction == Direction.UP or self.direction == Direction.DOWN:
            tile = np.transpose(tile)
        for n in range(len(tile)):
            for i in range(len(tile[n])):
                t = tile[n][i]
                if t in elemap:
                    self.grid[self.cursor[1] + n][self.cursor[0] + i] = CastleElement(
                        elemap[t]
                    )

    def turnClockwise(self):
        self.direction = Direction((self.direction + 1) % 4)

    def turnCounterClockwise(self):
        self.direction = Direction((self.direction - 1) % 4)

    def moveCursorInDirection(self, range=1):
        offset = self.directionToOffset[self.direction]
        self.cursor = (
            self.cursor[0] + offset[0] * range,
            self.cursor[1] + offset[1] * range,
        )


class CastleGenerator:
    def __init__(self, filepath, tilePath, width: int, height: int):
        self.tokenToElementType: dict[InstructionToken, ElementType] = {
            InstructionToken.KEEP: ElementType.KEEP,
            InstructionToken.WALL: ElementType.WALL,
            InstructionToken.GATE: ElementType.GATE,
            InstructionToken.TOWER: ElementType.TOWER,
        }
        self.tileMap = self.loadTileMap(tilePath)

        self.width = width  # // 3
        self.height = height  # // 3

        self.grid: list[list[None | CastleElement]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # Place keep in center
        self.center = (self.width // 2, self.height // 2)
        # self.grid[self.center[1]][self.center[0]] = CastleElement(ElementType.KEEP)

        self.generate(filepath)

    def loadTileMap(self, filepath: str):
        tileMap = {}
        for element in ElementType:
            with open(filepath + element.value + ".txt", "r") as f:
                tileMap[element] = [line.strip().split() for line in f]
            f.close()
        return tileMap

    def generate(self, filepath: str):
        self.instructionTree = parseInstructionTree(filepath)

        agents: list[CastleGenerationAgent] = []
        agents.append(
            CastleGenerationAgent(
                self.center, Direction.UP, self.instructionTree.root, self.grid
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

            if instruction == InstructionToken.LEFT:
                agent.turnCounterClockwise()
            elif instruction == InstructionToken.RIGHT:
                agent.turnClockwise()
            elif instruction == InstructionToken.BRANCH:
                agents.append(
                    CastleGenerationAgent(
                        agent.cursor,
                        agent.direction,
                        self.instructionTree.getNextChild(agent.instructionLine),
                        self.grid,
                    )
                )
            else:
                elementType = self.tokenToElementType[instruction]
                agent.placeNextElement(
                    self.tileMap[elementType], self.tokenToElementType
                )

    def getCastleMapInTerrainScale(self):
        scale = 1
        return [
            [cell for cell in row for _ in range(scale)]
            for row in self.grid
            for _ in range(scale)
        ]
