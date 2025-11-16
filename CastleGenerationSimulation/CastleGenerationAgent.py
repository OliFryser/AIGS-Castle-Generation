from CastleElement import CastleElement
from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionToken import InstructionToken
from Utils.Direction import Direction


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

    def placeNextElement(self, castleElement):
        self.moveCursorInDirection()
        self.grid[self.cursor[1]][self.cursor[0]] = CastleElement(castleElement)

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
