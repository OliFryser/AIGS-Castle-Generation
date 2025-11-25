import random
from pygame import Vector3
from queue import PriorityQueue
from Utils.Node import Node, Edge, Graph
import numpy as np

#get as node on Graph 2 gets the 3 closest nodes by distance
def getAsNodeOnGraph2(startPosition: Vector3 , graph: dict[Node, list[Edge]], tmpNodes,unit ,ignoreNodes):
    node = Node(startPosition)
    if node in graph:
        return node
    positions = sorted(graph.keys(), key=lambda node: node not in ignoreNodes and node.position.distance_to(startPosition))[:5]
    edges = []
    for tmpNode in positions:
        graph[tmpNode].append(Edge(node, tmpNode.position.distance_to(node.position)))
        tmpEdge = Edge(tmpNode, node.position.distance_to(tmpNode.position))
        edges.append(tmpEdge)

    graph[node] = edges
    tmpNodes.append(node)
    return node

#get as node on graph gets the four closest nodes directly from the graph
def getAsNodeOnGraph(startPosition: Vector3 , graph: Graph, tmpNodes, unit, ignoreNodes):
    node = Node(startPosition)
    if node in graph.graph:
        return node
    
    x, y, z = startPosition.x, startPosition.y, startPosition.z
    # Each coordinate is centered at 0.5 + int(n)
    x0 = np.floor(x - 0.5) + 0.5
    x1 = np.ceil(x - 0.5) + 0.5
    z0 = np.floor(z - 0.5) + 0.5
    z1 = np.ceil(z - 0.5) + 0.5

    positions = [
        Vector3(x0, y, z0),  # Northwest
        Vector3(x1, y, z0),  # Northeast
        Vector3(x0, y, z1),  # Southwest
        Vector3(x1, y, z1),  # Southeast
    ]

    edges = []
    for pos in positions:
        tmpNode = Node(pos)
        if tmpNode not in ignoreNodes and tmpNode in graph.graph:
            blockNode = graph.getNodeFromPosition(tmpNode.position)
            block = blockNode.materialBlock #type: ignore
            if block is not None and block.blocking:
                continue
            if blockNode is not None and blockNode.unit is not None and unit is not None and blockNode.unit != unit:
                continue
            graph.graph[tmpNode].append(Edge(node, tmpNode.position.distance_to(node.position)))
            tmpEdge = Edge(tmpNode, node.position.distance_to(tmpNode.position))
            edges.append(tmpEdge)

    graph.graph[node] = edges
    tmpNodes.append(node)
    return node

def getAsNodeOnGraph3(position, b: Graph, l,a,h):
    return b.getNodeFromPosition(position)

def distanceCost(node: Node, edge: Edge):
    return edge.cost

def euclidianDistance(node0: Node, node1: Node):
    return node0.position.distance_to(node1.position)

def aStar(startPosition: Vector3, targetPosition: Vector3, nodeGraph: Graph,
          heuristic = euclidianDistance, costAdjustFunc = distanceCost, budget = 1000, 
          ignoreNodes: list[Node] = [],
          unit = None,
          getFirstofType = None
          ):
    graph = nodeGraph.graph
    #pprint(graph.values())
    tmpNodes = []

    startNode = getAsNodeOnGraph(startPosition, nodeGraph, tmpNodes, unit, ignoreNodes)
    targetNode = getAsNodeOnGraph(targetPosition, nodeGraph, tmpNodes, unit, ignoreNodes)
    """
    print(startPosition,startNode,targetNode)
    startNode = nodeGraph.getNodeFromPosition(startPosition)
    targetNode = nodeGraph.getNodeFromPosition(targetPosition)
    """
    # distances is for storing the shortest distance to node
    distances: dict[Node, float] = {startNode: 0.0}
    open_nodes = PriorityQueue()
    # random is for tie-breaking distances random
    open_nodes.put(
        (
            heuristic(startNode, targetNode),
            np.random.rand(),
            startNode,
        )
    )

    # incomming nodes is for storing the shortest path between nodes
    incomming_nodes = {}
    
    while open_nodes.not_empty:
        # we only really need the next node
        _, r, currentNode = open_nodes.get()
        #print(currentNode.position,graph[currentNode])
        """
        if (currentNode.unit is not None and currentNode.unit is not unit):
            print(f" unit {currentNode.unit}, {unit}")
            print(f"price {distances[currentNode]}")
        """

        if (currentNode in ignoreNodes ):
            print("this should have been ignored")

        # if the next node is the target node the path has been set
        if distances[currentNode] > budget:
            #print(f"could not find path within budget {distances[currentNode], len(distances.keys())}")
            #print(currentNode.unit, currentNode.materialBlock.materialType)
            break

        if currentNode == targetNode or (
            getFirstofType is not None and 
            currentNode.materialBlock is not None and
            getFirstofType == currentNode.materialBlock.materialType            
            ):
            """
            print(f"path cost {distances[currentNode]}")
            """

            # backtrak to reconstruct path
            path = []
            while currentNode != startNode:
                path.insert(0, currentNode)
                #if currentNode.materialBlock is not None:
                    #path = []
                currentNode = incomming_nodes[currentNode]
            
            for node in tmpNodes:
                nodeGraph.removeNode(node)
            return path
        random.shuffle((graph[currentNode]))
        for edge in graph[currentNode]:
            #cost is calculated here
            cost = costAdjustFunc(currentNode, edge)
            """
            if cost > 200:
                print(cost)
                #continue
            """
                
            new_distance = distances[currentNode] + cost

            if edge.node in ignoreNodes or edge.node not in graph:
                print(f'Error node not in graph {edge.node.position}, start Node: {startNode.position}')
                continue
            if edge.node not in distances or new_distance < distances[edge.node]:
                distances[edge.node] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(edge.node, targetNode)
                incomming_nodes[edge.node] = currentNode
                open_nodes.put((predicted_total, np.random.rand(), edge.node))


    return []


def slopeAnglePercentage(distance: float, height0: float, height1: float) -> float:
    deltaHeight = height0 - height1
    return distance / np.sqrt(distance * distance + deltaHeight * deltaHeight)
