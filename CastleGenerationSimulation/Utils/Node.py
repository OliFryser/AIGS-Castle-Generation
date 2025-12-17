from pygame import Vector3
import numpy as np
from CastleElement import MaterialType
import gc


class Node:
    def __init__(self, position: Vector3) -> None:
        self.position = position
        self.position2 = (position.x,position.z)
        self.materialBlock = None
        self.unit = None
        self.asData = None #self.createData()
        
    def createData(self):
        return {
            "position" : (self.position.x, self.position.y, self.position.z),
            "position2" : self.position2,
            "materialBlock" : None if self.materialBlock is None else self.materialBlock.getAsData(),
            "unit" : None if self.unit is None else self.unit.getAsData(),
        }
    
    def destroy(self):
        self.position = None
        self.position2 = None
        self.unit = None
        if self.asData:
            self.asData = None
        
        if self.materialBlock is None:
            return
        self.materialBlock.nodeDeath()
        self.materialBlock = None
            
    def printRefs(self):
        gc.collect()
        refs = gc.get_referrers(self)
        for r in refs:
            if type(r) is not dict:
                print(type(r))
       
    def getAsData(self):
        return self.asData

    def setMaterialBlock(self, materialBlock):
        if materialBlock is None:
            return
        self.materialBlock = materialBlock
        materialBlock.node = self

    def setUnit(self, unit):
        self.unit = unit
        if self.asData:
            self.asData["unit"] = unit.getAsData()

    def clearUnit(self):
        self.unit = None
        if self.asData:
            self.asData["unit"] = None

    def __hash__(self) -> int:
        return hash((self.position.x,self.position.z))
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Node):
            return False
        return (self.position2 == value.position2)

class Edge:
    def __init__(self, node: Node, cost) -> None:
        self.node = node
        self.cost = cost
    
    def getAsData(self):
        return {
            "node": self.node.getAsData(), 
            "cost": self.cost}

    def purge(self):
        self.node = None

class Graph:
    def __init__(self) -> None:
        self.graph: dict[Node, list[Edge]] = {}
        self.nodes: dict[tuple[float,float], Node] = {}

    def getAsData(self):
        nodes = {key: node.getAsData() for key,node in self.nodes.items()}
        graph = {node.position2: list(e.getAsData() for e in edge) for node,edge in self.graph.items()}
        return {
            "graph" : graph,
            "nodes" : nodes,
        }

    def removeNode(self, toBeRemoved: Node):
        graph = self.graph
        if toBeRemoved not in graph:
            print(f"node {toBeRemoved.position} is not in graph")
            return
        edges = graph[toBeRemoved]
        for edge in edges:
            for neighbourEdge in graph[edge.node]:
                if neighbourEdge.node == toBeRemoved:
                    graph[edge.node].remove(neighbourEdge)
                    neighbourEdge.purge()
        del graph[toBeRemoved]
        if toBeRemoved.position2 in self.nodes:
            tmp = self.nodes[toBeRemoved.position2]
            tmp.destroy()
            del self.nodes[toBeRemoved.position2]
        #tmp.printRefs()

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