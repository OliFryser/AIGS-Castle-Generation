from pygame import Vector3
from Level import Level
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

    def __hash__(self) -> int:
        return hash((self.position.x,self.position.z))
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return (self.position2 == value.position2)
            
def createNodeGraph(level : Level, x = 0, y = 0):
    nodes = {}
    graph = {}
    for y in range(level.height -1):
        for x in range(level.width -1):
            node = Node(Vector3(x+ .5,level.getCell(x,y),y+.5))
            nodes[node.position2] = node
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
    return graph

def removeNode(toBeRemoved: Node, graph: dict[Node, list[Edge]]):
    if toBeRemoved not in graph:
        print(f"node {toBeRemoved.position} is not in graph")
        return
    edges = graph[toBeRemoved]
    for edge in edges:
        for nedge in graph[edge.node]:
            if nedge.node == toBeRemoved:
                graph[edge.node].remove(nedge)

    del graph[toBeRemoved]