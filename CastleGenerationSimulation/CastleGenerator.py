from collections import defaultdict
from enum import IntEnum
from pygame import Vector2
import queue
import numpy as np

from CastleElement import CastleElement, ElementType, MaterialType

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
        fromDirection: Direction | None = None,
        lastElement: CastleElement | None = None,
        ):
        # store the original instructions as each agent id. TODO: Wastes memory, could just be a number
        self.id = instructions

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
        # a collection of directions from whence it came
        if fromDirection is None:
            fromDirection = Direction((self.direction +2) % 4)
        self.fromDirection = fromDirection
        self.lastElement = lastElement

    def getNextInstruction(self) -> str | None:
        if len(self.instructions) <= 0:
            return None
        return self.instructions.pop()

    def placeNextElement(self, castleElement):
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
        
        self.fromDirection = Direction((self.direction +2) % 4)
        self.lastElement = cell

    def turnClockwise(self):
        # Add 1 modulo 4
        self.direction = Direction((self.direction + 1) % 4)
        self.fromDirection = Direction((self.fromDirection + 1) % 4)

    def turnCounterClockwise(self):
        # Subtract 1 modulo 4
        self.direction = Direction((self.direction - 1) % 4)
        self.fromDirection = Direction((self.fromDirection - 1) % 4)

    def moveCursorInDirection(self, range = 1):
        offset = self.directionToOffset[self.direction]
        self.cursor = (self.cursor[0] + offset[0] * range, self.cursor[1] + offset[1] * range)

class CastleGenerator:
    def __init__(self, filepath, tilePath, width: int, height: int, targetPositionx, targetPositiony):
        self.letterToElementType = {
            "K": ElementType.KEEP,
            "W": ElementType.WALL,
            "G": ElementType.GATE,
            "T": ElementType.TOWER,
        }
        
        self.directionToOffset = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
        }
        
        self.tileMap = self.loadTileMap(tilePath)
        self.scale = len(list(self.tileMap.values())[0][0])

        self.width = width
        self.height = height

        self.grid: list[list[None | CastleElement]] = [
            [None for _ in range(self.width // self.scale)] for _ in range(self.height // self.scale)
        ]

        # Place keep just above target
        self.center = (int((targetPositionx - self.scale/2)// self.scale), int((targetPositiony - self.scale/2)// self.scale))
        self.grid[self.center[1]][self.center[0]] = CastleElement(ElementType.KEEP)

        self.generate(filepath)

    def loadTileMap(self, filepath: str):
        tileMap = {}
        for element in ElementType:
            with open(filepath + element.value + ".txt", "r") as f:
                content = f.read().strip()
                tiles = [ [line.split() for line in block.splitlines()] 
                    for block in content.split('\n\n') ]
                tileMap[element] = tiles
                #print(tiles)
            f.close()
        return tileMap

    def generate(self, filepath: str):
        with open(filepath, "r") as f:
            self.instructions = [line.rstrip() for line in f]
            # Make sure we use real tabs
            self.convert4SpacesToTab()
        # evaluate the instructions, before they all get popped
        self.evaluateInstructions()
        # instruction dict. Each instruction maps to a list of its children
        self.generateInstructionTree(self.instructions)

        agents: list[CastleGenerationAgent] = []
        agents.append(
            CastleGenerationAgent(self.center, Direction.UP, self.root, self.grid)
        )

        while len(agents) > 0:
            self.step(agents)

    def evaluateInstructions(self):
        costMap = {
            "K": 5,
            "W": 1,
            "G": 3,
            "T": 5,
        }
        cost = 0
        for instruction in self.instructions:
            splitInstructions = instruction
            for splitInstruction in splitInstructions.split():
                if splitInstruction in costMap:
                    cost += costMap[splitInstruction]
        self.instructionCost = cost

    def getGateAmount(self, path):
        return self.gateCount

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
                        self.instructionTree[agent.id].get(),
                        self.grid,
                        agent.fromDirection,
                        agent.lastElement
                    )
                )
            else:
                elementType = self.letterToElementType[instruction]
                agent.placeNextElement(elementType)

    def generateInstructionTree(self, instructions: list[str]):
        self.instructionTree: defaultdict[str, queue.Queue[str]] = defaultdict(
            queue.Queue[str]
        )
        self.root = instructions[0]
        instructions.remove(self.root)

        parentStack = []
        lastInstruction = self.root
        level = 0
        for instruction in instructions:
            currentLevel = instruction.count("\t")
            # remove tabs here
            instruction = instruction.lstrip()
            if currentLevel > level:
                # go a level deeper
                level += 1
                parentStack.append(lastInstruction)
            if currentLevel < level:
                # go a level back
                level -= 1
                parentStack.pop()

            self.instructionTree[parentStack[-1]].put(instruction)
            lastInstruction = instruction

    def getCastleMapInTerrainScale(self, path):    
        grid = self.grid.copy()
        #self.addGates3(grid, path)
        gridToScale = np.full((self.height, self.width), None)
        for row in range(len(grid)):
            for column in range(len(grid[0])):
                if grid[row][column] is not None:
                    self.fillTile(grid[row][column], gridToScale, row*self.scale, column*self.scale)

        self.addGates(gridToScale, path)
        return gridToScale

    def addGates(self, gridToScale, path):
        self.gateCount = 0
        directionFrom = []
        previousPos = (0,0)
        for step in path:
            directionFrom = []
            newX = (step[0] - previousPos[0], 0)
            newY = (0, step[1] - previousPos[1])
            for direction, offset in self.directionToOffset.items():
                if newX == offset or newY == offset:
                    directionFrom.append(direction)
            previousPos = step

            cellElement = self.grid[step[1]][step[0]]
            if cellElement is not None:
                #if there is excactly two neighbours
                if len(cellElement.directions) == 2:
                    """
                    #setup new gate element
                    castleElement = CastleElement(ElementType.GATE, cellElement.column, cellElement.row)
                    castleElement.directions = cellElement.directions
                    #if the neighbours are perpendicular
                    #if (cellElement.directions[0] +2 )% 4 == cellElement.directions[1]:
                    print(castleElement.directions)
                    self.fillTile(castleElement, gridToScale, castleElement.column,castleElement.row)
                
                """
                for direction in cellElement.directions:
                    position = (step[0] * self.scale + self.directionToOffset[Direction(direction)][0] * 3, step[1] * self.scale + self.directionToOffset[Direction(direction)][1] * 2)
                    castleElement = CastleElement(ElementType.GATE, position[1],position[0])
                    castleElement.directions = [direction, (direction + 2) % 4]
                    self.fillTile(castleElement,gridToScale,position[1],position[0])
        pass

    def addGates3(self, grid, path):
        self.gateCount = 0
        for row in range(len(grid)):
            for column in range(len(grid[0])):
                if (column,row) in path:
                    grid[row][column] = CastleElement(ElementType.GATE)
                    if grid[row][column] is not None:
                        neighbours = self.castleElementNeighbors(row,column)
                        if len(neighbours) > 2 or not (len(neighbours) == 2 and set(neighbours) == set([Direction.DOWN,Direction.UP]) or set(neighbours) == set([Direction.LEFT,Direction.RIGHT])):
                            grid[row][column] = None    
                            continue
                        grid[row][column] = CastleElement(ElementType.GATE)
                        self.gateCount += 1

    #this assumes square tiles
    def fillTile(self, castleElement: CastleElement, grid, x, y):
        elementType = castleElement.elementType
        blockMap = self.tileMap[elementType]

        neighbors = castleElement.directions
        tile = self.morphATile(blockMap, neighbors)
        castleElement.column = x
        castleElement.row = y

        for column in range(len(tile)):
            for row in range(len(tile[column])):
                materialType = tile[column][row]
                if any (materialType == e.value for e in MaterialType):
                    #TODO adjust for printing empties regarding Gates
                    grid[x  + column][y + row] = castleElement
                    castleElement.setMaterialBlock(row,column, MaterialType(materialType))

    def morphATile(self, blocks, neighbors):
        #end bits
        if len(neighbors) == 1 and len(blocks) >= 5:
            if neighbors[0] == Direction.UP:
                return np.transpose(blocks[4])
            if neighbors[0] == Direction.DOWN:
                return np.flipud(np.transpose(blocks[4]))
            if neighbors[0] == Direction.RIGHT:
                return np.fliplr(blocks[4])
            return blocks[4]
        #Full four cornered neighbours
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

    def castleElementNeighbors(self, y, x, ignore: list[ElementType] = []):
        height = len(self.grid)
        width = len(self.grid[0])
        neighbors = []

        for direction, (dx, dy) in self.directionToOffset.items():
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < width:
                if self.grid[ny][nx] is not None and self.grid[ny][nx] not in ignore:
                    neighbors.append(direction)

        return neighbors

    def convert4SpacesToTab(self):
        for i, instruction in enumerate(self.instructions):
            self.instructions[i] = instruction.replace(" " * 4, "\t")
