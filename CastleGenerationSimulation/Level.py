import numpy as np
from pygame import Vector3

from CastleGenerator import CastleGenerator
from CastleInstructions.InstructionTree import InstructionTree
from TerrainMap import TerrainMap
from TileMap import TileMap
from Utils.Timer import Timer
from Utils.Node import Graph, Node, Edge
from Utils.PathFinding import aStar
from CastleElement import ElementType, MaterialType


class Level:
    def __init__(
        self,
        terrainMap: TerrainMap,
        castleInstructionTree: InstructionTree,
        tileMap: TileMap,
        targetPosition: Vector3 | None = None,
    ):
        self.terrainMap = terrainMap.map
        self.width = terrainMap.width
        self.height = terrainMap.height
        self.maxHeight = terrainMap.maxHeight
        self.castleMap = None
        if targetPosition is None:
            self.targetPosition = Vector3(
                self.width / 2 - 0.5,
                self.getBilinearHeight(self.width / 2 - 0.5, self.height / 2 - 0.5),
                self.height / 2 -0.5,
            )
        else:
            self.targetPosition = targetPosition

        timer = Timer("Castle generator")
        timer.start()
        castleGenerator = CastleGenerator(
            castleInstructionTree,
            tileMap,
            self.width,
            self.height,
            self.targetPosition.x,
            self.targetPosition.z,
        )
        timer.stop()

        positionPath = self.generatePath(castleGenerator)
        self.castleMap = castleGenerator.getCastleMapInTerrainScale(positionPath)

        timer = Timer("Node Graph")
        timer.start()
        self.nodeGraph: Graph = self.makeGraph(self.nodeToNodeDistance)
        timer.stop()

        #Debug print for path
        """
        for pos in positionPath:
            v3 = Vector3(
                pos[0]*castleGenerator.scale+castleGenerator.scale/2, 
                0, 
                pos[1]*castleGenerator.scale+castleGenerator.scale/2
            )
            print(v3)
            n = self.nodeGraph.getNodeFromPosition(v3)
            if n is not None:
                n.unit=1 #type: ignore
        """

        # gather data
        self.instructionCost = castleGenerator.cost
        self.gates = castleGenerator.getGateCount()
        self.castleCost = self.getCastleCost()
        self.protectedArea = self.getProtectedArea()

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
        nodeGraph = Graph()
        nodeGraph.graph, nodeGraph.nodes = self.createNodeGraph(edgeCostFunc, scale)
        return nodeGraph

    #  in an alternate universe you can look up by a tuple of x,z coordinates-> dict[tuple[float,float], dict[Node,list[Edge]]]
    #  but the graph class was better in the end instead of a super nested dict T_T
    def createNodeGraph(self, edgeCostFunc, scale: int):
        nodes = {}
        graph = {}
        for y in range(self.height // scale):
            for x in range(self.width // scale):
                node = Node(Vector3(x + 0.5, self.getCell(x, y), y + 0.5))
                nodes[node.position2] = node
                if self.castleMap is not None:
                    castleCell = self.castleMap[y][x]
                    if castleCell is not None:
                        material = castleCell.getMaterialBlockGlobal(x, y)
                        node.setMaterialBlock(material)
        for node in nodes.values():
            edges = []
            east = (node.position.x + 1, node.position.z)
            west = (node.position.x - 1, node.position.z)
            south = (node.position.x, node.position.z + 1)
            north = (node.position.x, node.position.z - 1)
            northEast = (east[0], north[1])
            northWest = (west[0], north[1])
            southEast = (east[0], south[1])
            southWest = (west[0], south[1])
            for cardinalNode in [
                east,
                west,
                north,
                northEast,
                northWest,
                southEast,
                southWest,
                south,
            ]:
                if cardinalNode in nodes:
                    tmpNode = nodes[cardinalNode]
                    tmpEdge = Edge(tmpNode, edgeCostFunc(node, tmpNode))
                    edges.append(tmpEdge)
            graph[node] = edges
        """
        print(
            f"Initiating node graph; level : {len(self.getLevel())} * {len(self.getLevel()[0])}, graph nodes: {len(graph.keys())}"
        )
        """
        return graph, nodes

    def nodeToNodeDistance(self, node0, node1):
        return node0.position.distance_to(node1.position)

    def pathCostAdjustFunc(self, node0: Node, node1: Node):
        diff = abs(node0.position.y - node1.position.y) * 10
        return node0.position.distance_to(node1.position) + diff

    def generatePath(self, castleGenerator: CastleGenerator):
        scale = castleGenerator.scale
        pathGraph = self.makeGraph(self.pathCostAdjustFunc, scale)
        home = Vector3(
                self.targetPosition.x / scale,
                self.targetPosition.y,
                self.targetPosition.z / scale,
            )
        nodePath = aStar(
            Vector3(
                self.width / scale /2,
                #0,
                self.getBilinearHeight(self.width / scale / 2, self.height / scale),
                self.height / scale,
                #self.height / scale/2,
                #0,
            ),
            home,
            pathGraph,
        )
        return [(int(node.position.x), int(node.position.z)) for node in nodePath] + [(self.targetPosition.x,self.targetPosition.z)]

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

    def getCastleCost(self):
        return self.instructionCost + self.gates * 3

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
                    # edge.node.unit = 1
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
                    and edge.node.materialBlock.castleElement is not None
                    and edge.node.materialBlock.castleElement.elementType
                    is ElementType.GATE
                ):
                    tmpGates.append(edge.node.position)

        return tempEnclosedNodes + enclosedNodes, tmpGates + gates
