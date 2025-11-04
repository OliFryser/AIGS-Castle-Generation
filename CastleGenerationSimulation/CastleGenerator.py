from enum import IntEnum
from time import sleep
from CastleElement import CastleElement, ElementType


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

    def placeNextElement(self, elementType: ElementType):
        self.moveCursorInDirection()
        self.grid[self.cursor[1]][self.cursor[0]] = CastleElement(elementType)

    def turnClockwise(self):
        # Add 1 modulo 4
        self.direction = Direction((self.direction + 1) % 4)

    def turnCounterClockwise(self):
        # Subtract 1 modulo 4
        self.direction = Direction((self.direction - 1) % 4)

    def moveCursorInDirection(self):
        offset = self.directionToOffset[self.direction]
        self.cursor = (self.cursor[0] + offset[0], self.cursor[1] + offset[1])


class CastleGenerator:
    def __init__(self, filepath, width: int, height: int):
        self.letterToElementType = {
            "K": ElementType.KEEP,
            "W": ElementType.WALL,
            "G": ElementType.GATE,
            "T": ElementType.TOWER,
        }

        self.width = width // 3
        self.height = height // 3

        self.grid: list[list[None | CastleElement]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        # Place keep in center
        self.center = (self.width // 2, self.height // 2)
        self.grid[self.center[1]][self.center[0]] = CastleElement(ElementType.KEEP)

        self.generate(filepath)

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
                agent.placeNextElement(elementType)

    def getCastleMapInTerrainScale(self):
        scale = 3
        return [
            [cell for cell in row for _ in range(scale)]
            for row in self.grid
            for _ in range(scale)
        ]
