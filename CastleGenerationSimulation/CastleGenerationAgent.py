from CastleElement import CastleElement
from CastleInstructions.InstructionToken import InstructionToken
from CastleInstructions.InstructionTree import TreeNode
from Utils.Direction import Direction


class CastleGenerationAgent:
    def __init__(
        self,
        cursor: tuple[int, int],
        initialDirection: Direction,
        treeNode: TreeNode,
        grid: list[list[None | CastleElement]],
        fromDirection: Direction | None = None,
        lastElement: CastleElement | None = None,
    ):
        self.treeNode = treeNode

        self.directionToOffset = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }

        self.cursor = cursor
        self.grid = grid
        self.direction = initialDirection

        # a collection of directions from whence it came
        if fromDirection is None:
            fromDirection = Direction((self.direction + 2) % 4)
        self.fromDirection = fromDirection
        self.lastElement = lastElement

        self.padding = 2

    def getNextInstruction(self) -> InstructionToken | None:
        if self.treeNode.line.isEmpty():
            return None
        return self.treeNode.line.getNextInstruction()

    def placeNextElement(self, castleElement):
        if self.isMovingOutOfBounds():
            return

        self.moveCursorInDirection()
        if self.lastElement is not None:
            if self.direction not in self.lastElement.directions:
                self.lastElement.directions.append(self.direction)

        cell = self.grid[self.cursor[1]][self.cursor[0]]
        if cell is None:
            cell = CastleElement(castleElement)
            self.grid[self.cursor[1]][self.cursor[0]] = cell

        if self.fromDirection is not None and self.fromDirection not in cell.directions:
            cell.directions.append(self.fromDirection)

        self.fromDirection = Direction((self.direction + 2) % 4)
        self.lastElement = cell

    def turnClockwise(self):
        # Add 1 modulo 4
        self.direction = Direction((self.direction + 1) % 4)
        self.fromDirection = Direction((self.fromDirection + 1) % 4)

    def turnCounterClockwise(self):
        # Subtract 1 modulo 4
        self.direction = Direction((self.direction - 1) % 4)
        self.fromDirection = Direction((self.fromDirection - 1) % 4)

    def moveCursorInDirection(self, range=1):
        offset = self.directionToOffset[self.direction]
        self.cursor = (
            self.cursor[0] + offset[0] * range,
            self.cursor[1] + offset[1] * range,
        )

    def isMovingOutOfBounds(self):
        height = len(self.grid)
        width = len(self.grid[0])

        offset = self.directionToOffset[self.direction]
        nextPosition = self.cursor[0] + offset[0], self.cursor[1] + offset[1]

        return not (
            nextPosition[0] >= self.padding
            and nextPosition[0] < width - self.padding
            and nextPosition[1] >= self.padding
            and nextPosition[1] < height - self.padding
        )
