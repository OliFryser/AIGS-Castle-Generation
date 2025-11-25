import numpy as np

from CastleElement import CastleElement, ElementType, MaterialType, tokenToElementType
from CastleGenerationAgent import CastleGenerationAgent
from CastleInstructions.InstructionToken import InstructionToken
from CastleInstructions.InstructionTree import InstructionTree
from TileMap import TileMap
from Utils.Direction import Direction, directionToOffset


class CastleGenerator:
    def __init__(
        self,
        castleInstructionTree: InstructionTree,
        tileMap: TileMap,  # noqa: F821
        width: int,
        height: int,
        targetPositionx,
        targetPositiony,
    ):
        self.padding = 2
        castleInstructionTree.reset()
        self.instructionTree: InstructionTree = castleInstructionTree

        self.tileMap = tileMap.tileMap
        self.scale = len(list(self.tileMap.values())[0][0])

        self.width = width
        self.height = height

        self.grid: list[list[None | CastleElement]] = [
            [None for _ in range(self.width // self.scale)]
            for _ in range(self.height // self.scale)
        ]

        self.center = (
            int((targetPositionx) // self.scale),
            int((targetPositiony) // self.scale) - 1,
        )
        self.centerOffset = (
            self.center[0] * self.scale - (targetPositionx - self.scale / 2),
            self.center[1] * self.scale - (targetPositiony - self.scale / 2),
        )

        # Place on top of Target
        """
        """
        keep = CastleElement(ElementType.KEEP)
        keep.directions = [Direction.LEFT, Direction.RIGHT, Direction.UP]
        self.grid[self.center[1]][self.center[0]] = keep

        self.evaluateInstructionCost()

        agents: list[CastleGenerationAgent] = []
        agents.append(
            CastleGenerationAgent(
                self.center,
                Direction.UP,
                self.instructionTree.root,
                self.grid,
                self.padding,
            )
        )

        while len(agents) > 0:
            self.step(agents)

    def getMaxArea(self):
        return self.getGridSize() * self.scale

    def countBlocks(self):
        count = 0
        for row in self.grid:
            for block in row:
                if block is not None:
                    count += 1
        return count

    def evaluateInstructionCost(self):
        self.cost = 0
        for instructionNode in self.instructionTree.nodes:
            self.cost += instructionNode.line.getCost()

    def getGateCount(self):
        return self.gateCount

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
                newBranch = self.instructionTree.getNextChild(agent.treeNode)
                if newBranch is None:
                    print("Wrongly formatted branching")
                else:
                    agents.append(
                        CastleGenerationAgent(
                            agent.cursor,
                            agent.direction,
                            newBranch,
                            self.grid,
                            self.padding,
                            agent.fromDirection,
                            agent.lastElement,
                        )
                    )
            else:
                elementType = tokenToElementType[instruction]
                agent.placeNextElement(elementType)

    def getGridSize(self):
        return (len(self.grid) - self.padding * 2) * (
            len(self.grid[0]) - self.padding * 2
        )

    def getCastleMapInTerrainScale(self, path):
        grid = self.grid.copy()
        self.clearCourtyard(grid)
        gridToScale = np.full((self.height, self.width), None)
        for row in range(len(grid)):
            for column in range(len(grid[0])):
                if grid[row][column] is not None:
                    if self.isBox(grid[row][column].elementType):
                        self.boxAdjust(grid[row][column], row, column)
                    self.fillTile(
                        grid[row][column],  # type: ignore
                        gridToScale,
                        row * self.scale,
                        column * self.scale,
                    )

        self.addGates(gridToScale, path)
        return gridToScale

    def boxAdjust(self, castleElement: CastleElement, row, column):
        for direction, offset in directionToOffset.items():
            if direction in castleElement.directions:
                continue
            neighbour = self.grid[row + offset[1]][column + offset[0]]
            if neighbour is None:
                continue
            if self.isBox(neighbour.elementType):
                castleElement.directions.append(direction)

    def isBox(self, elementType: ElementType):
        match elementType:
            case ElementType.TOWER:
                return True
            case ElementType.KEEP:
                return True
        return False

    def addGates(self, gridToScale, path):
        # path, pos = pathAndPos
        self.gateCount = 0
        directionFrom = []
        directionTo = []
        previousPos = (0, 0)
        onSide: tuple[Direction, Direction] = (Direction.DOWN, Direction.RIGHT)
        # purge path
        for p in path:
            if path.count(p) > 1:
                path.remove(p)

        for n in range(len(path) - 1):
            step = path[n]

            def travelDirections(pos0, pos1, inverse=False):
                tdirections = []
                newX = (np.sign(pos1[0] - pos0[0]), 0)
                newY = (0, np.sign(pos1[1] - pos0[1]))
                for direction, offset in directionToOffset.items():
                    if newX == offset or newY == offset:
                        if inverse:
                            direction = Direction((direction + 2) % 4)
                        tdirections.append(direction)
                if tdirections == []:
                    # print(pos0,pos1)
                    # return directionTo
                    pass
                return tdirections

            if n < len(path) - 2:
                directionTo = travelDirections(step, path[n + 1])
            else:
                directionTo = travelDirections(
                    (step[0] * self.scale, step[1] * self.scale), path[n + 1]
                )  # (path[n+1][0] - int(self.scale/2), path[n+1][1]- int(self.scale/2) ))

            directionFrom = travelDirections(previousPos, step, True)
            previousPos = step

            def switchSide(newSide, tonSide):
                if Direction.DOWN == newSide:
                    tonSide = (Direction.DOWN, tonSide[1])
                if Direction.UP == newSide:
                    tonSide = (Direction.UP, tonSide[1])
                if Direction.RIGHT == newSide:
                    tonSide = (tonSide[0], Direction.RIGHT)
                if Direction.LEFT is newSide:
                    tonSide = (tonSide[0], Direction.LEFT)
                return tonSide

            for d in directionFrom:
                onSide = switchSide(d, onSide)

            """
            print()
            print(f"{step} move towards {directionTo}, on side{onSide}")
            """

            # going towards a direction should check if that movement is blocked
            for moveDirection in directionTo:
                # if the direction of movement is the same as the side of the wall you are on, no worries
                if moveDirection not in onSide:
                    # however when moving to the side it isn't on a perpindicular wall on the on the same perpindicular side can block
                    if moveDirection in [Direction.UP, Direction.DOWN]:
                        side = onSide[1]
                    else:
                        side = onSide[0]

                    # if the path moves out of bounds, break
                    if step[1] >= len(self.grid) or step[0] >= len(self.grid[0]):
                        break
                    cellElement = self.grid[step[1]][step[0]]
                    # if a castleElement is present
                    if cellElement is not None:
                        # if there is only one connection, it can be sidestepped
                        if len(cellElement.directions) <= 1:
                            """
                            print("move around")
                            """
                            continue
                        # otherwise the wall in that direction will need a door
                        if side in cellElement.directions:
                            self.gateCount += 1
                            # if it is a straight wall then it should be trivial
                            position = (step[0] * self.scale, step[1] * self.scale)
                            if set(cellElement.directions) == set(
                                [Direction.UP, Direction.DOWN]
                            ) or set(cellElement.directions) == set(
                                [Direction.LEFT, Direction.RIGHT]
                            ):
                                connections = cellElement.directions
                                castleElement = CastleElement(
                                    ElementType.GATE, position[1], position[0]
                                )
                                castleElement.directions = connections
                                self.fillTile(
                                    castleElement, gridToScale, position[1], position[0]
                                )
                            # otherwise the gate needs to be pushed a bit, place half, and then force the neighbor to take the other half
                            else:
                                position2 = (
                                    step[0] * self.scale
                                    + directionToOffset[Direction(side)][0]
                                    * self.scale,
                                    step[1] * self.scale
                                    + directionToOffset[Direction(side)][1]
                                    * self.scale,
                                )
                                # get the special half gate block
                                block = self.tileMap[ElementType.GATE][1]
                                castleElement = CastleElement(
                                    ElementType.GATE, position[1], position[0]
                                )
                                connections = [side]
                                if side in [Direction.DOWN, Direction.RIGHT]:
                                    block = np.fliplr(block)
                                    castleElement = CastleElement(
                                        ElementType.GATE, position2[1], position2[0]
                                    )
                                    connections = [Direction((side + 2) % 4)]

                                castleElement.directions = connections
                                self.fillTile(
                                    castleElement,
                                    gridToScale,
                                    position[1],
                                    position[0],
                                    block,
                                )
                                castleElement.directions = [
                                    Direction((connections[0] + 2) % 4)
                                ]
                                self.fillTile(
                                    castleElement,
                                    gridToScale,
                                    position2[1],
                                    position2[0],
                                    np.fliplr(block),
                                )

                            """                            
                            for k,mb in castleElement.materialBlocks.items():    
                                print(k,mb.materialType)
                            print(f"built gate {side.name}")
                            """
                # eventually
                onSide = switchSide(moveDirection, onSide)
                """
                print(f"switching side from {moveDirection.name} {onSide}")
                print(directionTo)
                """

    def clearCourtyard(self, grid):
        courtyard = (self.center[0], self.center[1] + 1)
        cell = grid[courtyard[1]][courtyard[0]]
        print(courtyard)
        if cell is None:
            return
        for direction in cell.directions:
            tmpPosition = (
                courtyard[0] + directionToOffset[direction][0],
                courtyard[1] + directionToOffset[direction][1],
            )
            tmpCell = grid[tmpPosition[1]][tmpPosition[0]]
            direct = Direction((direction + 2) % 4)
            if direct in tmpCell.directions:
                tmpCell.directions.remove(direct)
        grid[courtyard[1]][courtyard[0]] = None

    # this assumes square tiles
    def fillTile(self, castleElement: CastleElement, grid, x, y, block=None):
        elementType = castleElement.elementType
        if block is None:
            blockMap = self.tileMap[elementType]
        else:
            blockMap = [block]

        neighbors = castleElement.directions
        tile = self.morphATile(blockMap, neighbors)
        castleElement.column = x - int(self.scale / 2)
        castleElement.row = y - int(self.scale / 2)

        for column in range(len(tile)):
            for row in range(len(tile[column])):
                materialType = tile[column][row]
                if any(materialType == e.value for e in MaterialType):
                    grid[x - int(self.scale / 2) + column][
                        y - int(self.scale / 2) + row
                    ] = castleElement
                    castleElement.setMaterialBlock(
                        row, column, MaterialType(materialType)
                    )

    def morphATile(self, blocks, neighbors):
        # end bits
        if len(neighbors) == 1 and len(blocks) >= 5:
            if neighbors[0] == Direction.UP:
                return np.transpose(blocks[4])
            if neighbors[0] == Direction.DOWN:
                return np.flipud(np.transpose(blocks[4]))
            if neighbors[0] == Direction.RIGHT:
                return np.fliplr(blocks[4])
            return blocks[4]
        # Full four cornered neighbours
        if len(neighbors) == 4 and len(blocks) >= 4:
            return blocks[3]
        # T section
        if len(neighbors) == 3 and len(blocks) >= 3:
            if Direction.UP not in neighbors:
                return blocks[2]
            if Direction.DOWN not in neighbors:
                return np.flipud(blocks[2])
            if Direction.LEFT not in neighbors:
                return np.transpose(blocks[2])
            if Direction.RIGHT not in neighbors:
                return np.fliplr(np.transpose(blocks[2]))
        # Two neighbors
        if len(neighbors) == 2 and len(blocks) >= 2:
            # Corner
            if Direction.LEFT in neighbors and Direction.DOWN in neighbors:
                return blocks[1]
            if Direction.LEFT in neighbors and Direction.UP in neighbors:
                return np.flipud(blocks[1])
            if Direction.RIGHT in neighbors and Direction.DOWN in neighbors:
                return np.fliplr(blocks[1])
            if Direction.RIGHT in neighbors and Direction.UP in neighbors:
                return np.transpose(blocks[1])
        # Straight bit
        if Direction.UP in neighbors or Direction.DOWN in neighbors:
            return np.transpose(blocks[0])
        # Default
        return blocks[0]
