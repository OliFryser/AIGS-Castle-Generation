import numpy as np
from pygame import Vector3

from CastleGenerator import CastleGenerator
from Utils.Timer import Timer
from Utils.Node import Graph,Node,Edge

class Level:
    def __init__(self, levelFilepath: str, castleGenerationFilepath: str, castleTilesFilePath: str):
        self.createTerrainMap(levelFilepath)

        timer = Timer("Castle generator")
        timer.start()
        castleGenerator = CastleGenerator(
            castleGenerationFilepath, castleTilesFilePath, self.width, self.height
        )
        timer.stop()

        self.castleMap = castleGenerator.getCastleMapInTerrainScale()
        
        timer = Timer("Node Graph")
        timer.start()
        self.nodeGraph = self.makeGraph()
        timer.stop()

    def createTerrainMap(self, levelFilepath: str):
        with open(levelFilepath, "r") as f:
            self.width, self.height, self.max_height = [
                int(x) for x in f.readline().rstrip().split()
            ]
            self.terrainMap = np.zeros((self.height, self.width))
            for y in range(self.height):
                line = [float(num) for num in f.readline().rstrip().split()]
                for x in range(self.width):
                    self.terrainMap[y][x] = line[x]

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
    
    def makeGraph(self):
        nodeGraph = Graph()
        print(nodeGraph)
        nodeGraph.graph, nodeGraph.nodes = self.createNodeGraph()
        print(nodeGraph)
        return nodeGraph

    #  in an alternate universe you can look up by a tuple of x,z coordinates-> dict[tuple[float,float], dict[Node,list[Edge]]]
    #  but the graph class was better in the end instead of a super nested dict T_T
    def createNodeGraph(self):
        nodes = {}
        graph = {}
        for y in range(self.height):
            for x in range(self.width):
                node = Node(Vector3(x+ .5,self.getCell(x,y),y+.5))
                nodes[node.position2] = node
                castleCell = self.castleMap[y][x]
                if castleCell is not None:
                    material = castleCell.getMaterialBlockGlobal(x,y)
                    node.setMaterialBlock(material)
        for node in nodes.values():
                edges = []
                east = (node.position.x +1, node.position.z)
                west = (node.position.x -1, node.position.z)
                south = (node.position.x, node.position.z +1)
                north = (node.position.x,node.position.z -1)
                northEast = (east[0], north[1])
                northWest = (west[0], north[1])
                southEast = (east[0], south[1])
                southWest = (west[0], south[1])
                for v2 in [east,west,south,north,northEast,northWest,southEast,southWest]:
                    if v2 in nodes:
                        tmpNode = nodes[v2]
                        tmpEdge = Edge(tmpNode, node.position.distance_to(tmpNode.position))
                        edges.append(tmpEdge)
                graph[node] = edges
        print(f"Initiating node graph; level : {len(self.getLevel())} * {len(self.getLevel()[0])}, graph nodes: {len(graph.keys())}")
        return graph, nodes