from pygame import Vector3
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

    def setMaterialBlock(self, materialBlock):
        self.materialBlock = materialBlock
        materialBlock.node = self

    def __hash__(self) -> int:
        return hash((self.position.x,self.position.z))
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return (self.position2 == value.position2)
    
class Graph:
    def __init__(self) -> None:
        self.graph: dict[Node, list[Edge]] = {}
        self.nodes: dict[tuple[float,float], Node] = {}

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