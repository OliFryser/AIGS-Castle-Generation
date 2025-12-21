import numpy as np
from pygame import Vector2, Vector3

from CastleGenerator import CastleGenerator
from CastleInstructions.InstructionTree import InstructionTree
from TerrainMap import TerrainMap
from TileMap import TileMap
from Utils.Timer import Timer
from Utils.Node import Graph, Node, Edge
from Utils.PathFinding import aStar
from CastleElement import ElementType, MaterialType, MaterialBlock

class Level:
    def __init__(
        self,
        terrainMap: TerrainMap,
        tileMap: TileMap,
    ):

        self.terrainMap = terrainMap.map
        self.waterMap = terrainMap.waterMap
        self.width = terrainMap.width
        self.height = terrainMap.height
        self.maxHeight = terrainMap.maxHeight
        targetPosition = terrainMap.target
        self.castleMap = None
        self.tileMap = tileMap
        
        self.scale = tileMap.scale

        #the scale division multiplication adjusts the target to be in line with the castlemap
        if targetPosition is None:
            x = int(self.width / 2)// self.scale * self.scale
            z = int(self.height / 3)// self.scale * self.scale
        else:
            x = targetPosition[0]//self.scale * self.scale
            z = targetPosition[1]//self.scale * self.scale
        self.targetPosition = Vector3(
            x,
            self.getBilinearHeight(x, z),
            z,
        )


        timer = Timer("Node Graph")
        timer.start()
        self.nodeGraph: Graph = self.makeGraph(self.nodeToNodeDistance)
        timer.stop()

        self.pathZero = terrainMap.path


    def makeCastle(self, castleInstructionTree):

        timer = Timer("Castle generator")
        timer.start()
        castleGenerator = CastleGenerator(
            castleInstructionTree,
            self.tileMap,
            self.width,
            self.height,
            self.targetPosition.x,
            self.targetPosition.z,
        )
        timer.stop()

        self.castleMapDuplo = castleGenerator.grid
        self.scale = castleGenerator.scale

        self.path = self.inferPathOrder(self.pathZero)

        self.castleMap = castleGenerator.getCastleMapInTerrainScale(self.path)

        timer = Timer("Adding castle to Node Graph")
        timer.start()
        self.addCastleNodes(self.nodeToNodeDistance)
        #self.navigationGraph = self.nodeGraph.getAsData()
        timer.stop()

        # gather data
        self.instructionCost = castleGenerator.cost
        self.gates = castleGenerator.getGateCount()
        self.blocks = castleGenerator.countBlocks()
        self.blockCount = self.countBlocks()
        self.towerRatio = self.getTowerRatio()
        self.protectedArea = self.getProtectedArea()
        self.castleCost = castleGenerator.countBlockCost()
        self.maxBlocks = castleGenerator.getGridSize()
        self.maxArea = castleGenerator.getMaxArea()
        self.orientationRatios()



    def countBlocks(self):
        count = 0
        for value in self.blocks.values():
            count += value
        return count
    
    def getTowers(self):
        if ElementType.TOWER in self.blocks:
            return self.blocks[ElementType.TOWER]
        return 0
    
    def orientationRatios(self):
        keepPos = (0,0)
        positions = []
        for column in range(len(self.castleMapDuplo)):
            for row in range(len(self.castleMapDuplo[column])):
                if self.castleMapDuplo[column][row] is None:
                    continue
                if self.castleMapDuplo[column][row].elementType is ElementType.KEEP:
                    keepPos = (row, column)
                    continue
                positions.append((row,column))

        east = 0 
        west = 0 
        north = 0
        south = 0

        kx, ky = keepPos

        for x, y in positions:
            if x > kx:
                east += 1
            elif x < kx:
                west += 1

            if y > ky:
                north += 1
            elif y < ky:
                south += 1

        ewDivider = east + west
        nsDivider = north + south

        self.eastWestRatio = east / ewDivider if ewDivider else 0.5
        self.northSouthRatio = north / nsDivider if nsDivider else 0.5

    def getTowerRatio(self):
        if ElementType.TOWER not in self.blocks:
            return 0
        if ElementType.WALL not in self.blocks:
            return 1
        return self.blocks[ElementType.TOWER] / self.blocks[ElementType.WALL]

    def getLevel(self):
        return self.terrainMap

    def getCell(self, x, y):
        return float(self.terrainMap[y][x])

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
        # Identify the four nearest cell indices
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        x1 = x0 + 1
        y1 = y0 + 1

        # Bounds guard
        max_y, max_x = self.height, self.width
        x0 = np.clip(x0, 0, max_x - 1)
        x1 = np.clip(x1, 0, max_x - 1)
        y0 = np.clip(y0, 0, max_y - 1)
        y1 = np.clip(y1, 0, max_y - 1)

        # Fractional position relative to the cell centers
        tx = x - (x0 + 0.5) + 0.5
        ty = y - (y0 + 0.5) + 0.5

        # Clamp to [0, 1] to avoid distant cells dominating
        tx = np.clip(tx, 0.0, 1.0)
        ty = np.clip(ty, 0.0, 1.0)

        # Standard bilinear interpolation
        h00 = self.getCell(x0, y0)
        h10 = self.getCell(x1, y0)
        h01 = self.getCell(x0, y1)
        h11 = self.getCell(x1, y1)

        return (
            h00 * (1 - tx) * (1 - ty)
            + h10 * tx * (1 - ty)
            + h01 * (1 - tx) * ty
            + h11 * tx * ty
        )

    #####################################################
    # Node Graph and castle path generation
    #####################################################

    def makeGraph(self, edgeCostFunc, scale: int = 1):
        #nodeGraph = Graph()
        #nodeGraph.graph, nodeGraph.nodes = self.createNodeGraph(edgeCostFunc, scale)
        nodeGraph = self.createNodeGraph(edgeCostFunc,scale)
        return nodeGraph

    #  in an alternate universe you can look up by a tuple of x,z coordinates-> dict[tuple[float,float], dict[Node,list[Edge]]]
    #  but the graph class was better in the end instead of a super nested dict T_T
    def createNodeGraph(self, edgeCostFunc, scale: int):
        nodeGraph = Graph()
        nodes = {}
        graph = {}
        nodeGraph.graph = graph
        nodeGraph.nodes = nodes
        for y in range(self.height // scale):
            for x in range(self.width // scale):
                node = Node(Vector3(x + 0.5, self.getCell(x, y), y + 0.5))
                nodes[node.position2] = node
                """
                if self.castleMap is not None:
                    castleCell = self.castleMap[y][x]
                    if castleCell is not None:
                        material = castleCell.getMaterialBlockGlobal(x, y)
                        node.setMaterialBlock(material)
                """
                
                if (x,y) in self.waterMap:
                    node.setMaterialBlock(MaterialBlock(MaterialType.WATER))


        for node in nodes.values():
            nodeGraph.addNode(node,edgeCostFunc)
        """
        print(f"Initiating node graph; level : {len(self.getLevel())} * {len(self.getLevel()[0])}, graph nodes: {len(graph.keys())}")
        """
        return nodeGraph
    
    def addCastleNodes(self, edgeCostFunc):
        for y in range(self.height):
            for x in range(self.width):
                if self.castleMap is not None:
                    castleCell = self.castleMap[y][x]
                    if castleCell is not None:
                        node = Node(Vector3(x + 0.5, self.getCell(x, y), y + 0.5))
                        material = castleCell.getMaterialBlockGlobal(x, y)
                        node.setMaterialBlock(material)
                        self.nodeGraph.removeNode(node)
                        self.nodeGraph.addNode(node, edgeCostFunc)
       

    def clearCastle(self):
        tobeRemoved = []
        for node in self.nodeGraph.nodes.values():
            node.clearUnit()
            if node.position is not None and node.materialBlock is not None and node.materialBlock.materialType is not MaterialType.WATER:
                tobeRemoved.append(node)
                
        for node in tobeRemoved:    
            newNode = Node(node.position)
            if newNode.position2 in self.waterMap:
                newNode.setMaterialBlock(MaterialBlock(MaterialType.WATER))
            self.nodeGraph.removeNode(node)
            self.nodeGraph.addNode(newNode, self.nodeToNodeDistance)

    def nodeToNodeDistance(self, node0, node1):
        return node0.position.distance_to(node1.position)

    def pathCostAdjustFunc(self, node0: Node, node1: Node):
        diff = abs(node0.position.y - node1.position.y) * 10
        return node0.position.distance_to(node1.position) + diff

    def generatePath(self):
        scale = self.scale
        pathGraph = self.makeGraph(self.pathCostAdjustFunc, scale)
        home = Vector3(
            self.targetPosition.x / scale,
            self.targetPosition.y,
            self.targetPosition.z / scale,
        )
        nodePath = aStar(
            Vector3(
                self.width / scale / 2,
                # 0,
                self.getBilinearHeight(self.width / scale / 2, self.height / scale),
                self.height / scale - 1,
                # self.height / scale/2,
                # 0,
            ),
            home,
            pathGraph,
        )
        return [(int(node.position.x), int(node.position.z)) for node in nodePath] + [
            (self.targetPosition.x, self.targetPosition.z)
        ]
    
    def inferPathOrder(self, path):
        point = Vector2(self.targetPosition.x,self.targetPosition.z)
        newPath = [point]
        tmpPath = [Vector2(p) for p in path]
        while tmpPath != []:
            point = min(tmpPath, key=lambda x: point.distance_to(x))
            newPath.append(point)
            tmpPath.remove(point)

        return [(int(p.x//self.scale),int(p.y//self.scale)) for p in newPath]

    ##############################################################
    # Behaviour
    ##############################################################

    def getProtectedArea(self):
        enclosed = []
        checkedGates = []
        gates = [self.targetPosition]
        while gates != []:
            gate = gates.pop()
            if gate not in checkedGates:
                checkedGates.append(gate)
                enclosed, gates = self.getEnclosedNodes(gate, enclosed, gates)

        return len(enclosed)

    def getEnclosedNodes(self, startPosition, enclosedNodes, gates):
        currentNode = self.nodeGraph.getNodeFromPosition(startPosition)

        tempEnclosedNodes = [currentNode]
        openNodes = [currentNode]
        tmpGates = []

        while openNodes != []:
            currentNode = openNodes.pop()
            if currentNode is None:
                continue

            for edge in self.nodeGraph.graph[currentNode]:
                if (
                    (
                        edge.node.materialBlock is None
                        or (
                            edge.node.materialBlock is not None
                            and not edge.node.materialBlock.blocking
                        )
                    )
                    and edge.node not in tempEnclosedNodes
                    and edge.node not in enclosedNodes
                ):
                    tempEnclosedNodes.append(edge.node)
                    openNodes.append(edge.node)
                    #edge.node.unit = 1
                if edge.node is None:
                    continue
                # if touching an edge, don't count erea as being enclosed
                if (
                    edge.node.position.x < 1
                    or edge.node.position.x > self.width - 1
                    or edge.node.position.z < 1
                    or edge.node.position.z > self.height - 1
                ):
                    return enclosedNodes, gates
                if (
                    edge.node not in tmpGates
                    and edge.node.materialBlock is not None
                    and edge.node.materialBlock.materialType == MaterialType.DOOR
                    #and edge.node.materialBlock.castleElement is not None
                    #and edge.node.materialBlock.castleElement.elementType is ElementType.GATE
                ):
                    tmpGates.append(edge.node.position)

        return tempEnclosedNodes + enclosedNodes, tmpGates + gates
