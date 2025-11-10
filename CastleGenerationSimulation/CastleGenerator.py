from collections import defaultdict
from enum import IntEnum
import queue
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

    def getNextInstruction(self) -> str | None:
        if len(self.instructions) <= 0:
            return None
        return self.instructions.pop()

    def placeNextElement(self, castleElement):
        self.moveCursorInDirection()
        self.grid[self.cursor[1]][self.cursor[0]] = CastleElement(castleElement)

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

        # Place keep in center
        self.center = ((self.width // self.scale) // 2, (self.height // self.scale) // 2 - 1)
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

        # instruction dict. Each instruction maps to a list of its children
        self.generateInstructionTree(self.instructions)

        agents: list[CastleGenerationAgent] = []
        agents.append(
            CastleGenerationAgent(self.center, Direction.UP, self.root, self.grid)
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
                        self.instructionTree[agent.id].get(),
                        self.grid,
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

    def getCastleMapInTerrainScale(self):    

        gridToScale = np.full((self.height, self.width), None)
        for row in range(len(self.grid)):
            for column in range(len(self.grid[0])):
                if self.grid[row][column] is not None:
                    self.fillTile(self.grid[row][column].elementType, gridToScale, row, column)


        return gridToScale

    
    #this assumes square tiles
    def fillTile(self,castleElement, grid, x, y):  
        blockMap = self.tileMap[castleElement]
        tile = self.morphATile(blockMap, x, y)

        for column in range(len(tile)):
            for row in range(len(tile[column])):
                t  = tile[column][row]                
                if t in self.letterToElementType.keys():
                    grid[x * self.scale+ column][y*self.scale + row] = CastleElement(self.letterToElementType[t])

    def morphATile(self, blocks, x, y):
        neighbors = self.castleElementNeighbors(x,y)
        if len(neighbors) == 4 and len(blocks) >= 4:
            return blocks[3]
        if len(neighbors) == 3 and len(blocks) >= 3:
            if Direction.UP not in neighbors:
                return blocks[2]
            if Direction.DOWN not in neighbors:
                return np.flipud(blocks[2])
            if Direction.LEFT not in neighbors:
                return np.transpose(blocks[2])
            if Direction.RIGHT not in neighbors:
                return np.fliplr(np.transpose(blocks[2]))
        if len(neighbors) == 2 and len(blocks) >= 2:
            if Direction.LEFT in neighbors and Direction.DOWN in neighbors:              
                return blocks[1]
            if Direction.LEFT in neighbors and Direction.UP in neighbors:
                return np.flipud(blocks[1])
            if Direction.RIGHT in neighbors and Direction.DOWN in neighbors:
                return np.fliplr(blocks[1])
            if Direction.RIGHT in neighbors and Direction.UP in neighbors:
                return np.transpose(blocks[1])
        if Direction.UP in neighbors or Direction.DOWN in neighbors:
         
            return np.transpose(blocks[0])
        return blocks[0]


    def castleElementNeighbors(self, y, x):
        height = len(self.grid)
        width = len(self.grid[0])
        neighbors = []

        for direction, (dx, dy) in self.directionToOffset.items():
            nx, ny = x + dx, y + dy
            if 0 <= ny < height and 0 <= nx < width:
                if self.grid[ny][nx] is not None:
                    neighbors.append(direction)

        return neighbors

    def convert4SpacesToTab(self):
        for i, instruction in enumerate(self.instructions):
            self.instructions[i] = instruction.replace(" " * 4, "\t")
