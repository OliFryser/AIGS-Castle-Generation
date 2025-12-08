from pygame import Vector3
import numpy as np
from CastleElement import MaterialType

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
        if materialBlock is None:
            return
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
        del self.nodes[toBeRemoved.position2]

    def getNodeFromPosition(self, position: Vector3):
        nodeid = (np.floor(position.x)+0.5, np.floor(position.z) +0.5)
        if nodeid in self.nodes:
            return self.nodes[nodeid]
        
    def addNode(self, toBeAdded: Node, edgeCostFunc):
        newNode = False
        if toBeAdded in self.graph:
            print(f"node {toBeAdded.position2} already in Graph")
            return
        if toBeAdded.position2 not in self.nodes:
            newNode = True
            self.nodes[toBeAdded.position2] = toBeAdded
        if toBeAdded.materialBlock is not None and not (toBeAdded.materialBlock.materialType is MaterialType.DOOR or toBeAdded.materialBlock.materialType is MaterialType.PAVEMENT):
            self.graph[toBeAdded] = []
            return
        edges = []
        east = (toBeAdded.position.x + 1, toBeAdded.position.z)
        west = (toBeAdded.position.x - 1, toBeAdded.position.z)
        south = (toBeAdded.position.x, toBeAdded.position.z + 1)
        north = (toBeAdded.position.x, toBeAdded.position.z - 1)
        #northEast = (east[0], north[1])
        #northWest = (west[0], north[1])
        #southEast = (east[0], south[1])
        #southWest = (west[0], south[1])
        for cardinalNode in [
            east,
            west,
            north,
            #northEast,
            #northWest,
            #southEast,
            #southWest,
            south,
        ]:
            if cardinalNode in self.nodes:
                tmpNode = self.nodes[cardinalNode]
                if tmpNode.materialBlock is not None and not (tmpNode.materialBlock.materialType is MaterialType.DOOR or tmpNode.materialBlock.materialType is MaterialType.PAVEMENT):
                    continue
                    pass
                tmpEdge = Edge(tmpNode, edgeCostFunc(toBeAdded, tmpNode))
                edges.append(tmpEdge)
                #maybe there is no return edge, in which case
                if newNode:
                    goon = Edge(toBeAdded, edgeCostFunc(tmpNode, toBeAdded))
                    self.graph[tmpNode].append(goon)

        self.graph[toBeAdded] = edges