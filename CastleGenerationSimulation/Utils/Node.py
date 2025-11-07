from pygame import Vector2,Vector3
from Level import Level
from CastleElement import MaterialBlock
import numpy as np

class Edge:
    def __init__(self, node, cost) -> None:
        self.node = node
        self.cost = cost

class Node:
    def __init__(self, position: Vector3) -> None:
        self.neighbours = {}
        self.position = position
        self.position2 = (position.x,position.z)
        self.materialBlock = None
        self.unit = None

    def setMaterialBlock(self, materialBlock: MaterialBlock):
        self.materialBlock = materialBlock

    ##
    # this is a good idea, but slightly annoying you can't get a key by a key from a dict, then it loses a bit of usability
    ##
    def __hash__(self) -> int:
        return hash((self.position.x,self.position.z))
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return (self.position2 == value.position2)
    
class Graph:
    def __init__(self, level: Level) -> None:
        self.graph: dict[Node, list[Edge]] = {}
        self.nodes: dict[tuple[float,float], Node] = {}
        self.graph, self.nodes = createNodeGraph(level)

    def removeNode(self, toBeRemoved: Node):
        graph = self.graph
        if toBeRemoved not in graph:
            print(f"node {toBeRemoved.position} is not in graph")
            return
        edges = graph[toBeRemoved]
        for edge in edges:
            for nedge in graph[edge.node]:
                if nedge.node == toBeRemoved:
                    graph[edge.node].remove(nedge)

        del graph[toBeRemoved]

    def getNodeFromPosition(self, position: Vector3):
        nodeid = (np.floor(position.x)+0.5, np.floor(position.z) +0.5)
        if nodeid in self.nodes:
            return self.nodes[nodeid]
    
#  in an alternate universe you can look up by a tuple of x,z coordinates-> dict[tuple[float,float], dict[Node,list[Edge]]]
#  but the graph class was better in the end instead of a super nested dict T_T
def createNodeGraph(level : Level):
    nodes = {}
    graph = {}
    for y in range(level.height):
        for x in range(level.width):
            node = Node(Vector3(x+ .5,level.getCell(x,y),y+.5))
            nodes[node.position2] = node
            castleCell = level.castleMap[y][x]
            if castleCell is not None:
                node.setMaterialBlock(castleCell.material)
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
            #graph[node.position2] = {node: edges}
            graph[node] = edges
    print(f"Initiating node graph; level : {len(level.getLevel())} * {len(level.getLevel()[0])}, graph nodes: {len(graph.keys())}")
    return graph, nodes

def createHexNodeGrap(level: Level):
    nodes = {}
    graph = {}
    vert = 2
    hori = 4
    row, y= 0,0
    while y < level.height -1:
        column, x = 0,0
        while x < level.width -1:
            node = Node(Vector3(x+ .5,level.getCell(x,y),y+.5))
            nodes[node.position2] = node
            x =  column *hori + 2 * (row % 2)
            column += 1
        y = row *vert
        row +=1

    for node in nodes.values():
            edges = []
            #it looks scetchy that it uses hori for vertical movement and vice verca, but it saves multiplying and dividing
            # as the results amount to the same
            east = (node.position.x +hori, node.position.z)
            west = (node.position.x -hori, node.position.z)
            south = (node.position.x, node.position.z +hori)
            north = (node.position.x,node.position.z -hori)
            northEast = (node.position.x + vert, node.position.z - vert)
            northWest = (node.position.x - vert, node.position.z - vert)
            southEast = (node.position.x + vert, node.position.z + vert)
            southWest = (node.position.x - vert, node.position.z + vert)
            for v2 in [east,west,south,north,northEast,northWest,southEast,southWest]:
                if v2 in nodes:
                    tmpNode = nodes[v2]
                    tmpEdge = Edge(tmpNode, node.position.distance_to(tmpNode.position))
                    edges.append(tmpEdge)
            #print(edges)
            graph[node.position2] = {node: edges}
            #graph[node] = edges

    print(len(level.getLevel()),len(level.castleMap),len(graph.keys()))
    return graph, nodes


def getHexSquares(x: float, y: float):
    return [
                                (int(x- 0.5), int(y- 1.5)), (int(x+ 0.5), int(y- 1.5)),
     (int(x- 1.5), int(y- 0.5)),(int(x- 0.5), int(y- 0.5)), (int(x+ 0.5), int(y- 0.5)), (int(x+ 1.5), int(y- 0.5)),
                                (int(x- 0.5), int(y+ 1.5)), (int(x+ 0.5), int(y+ 1.5)),
            
    ]


