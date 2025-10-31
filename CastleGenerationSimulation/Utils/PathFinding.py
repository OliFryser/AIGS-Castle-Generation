from pygame import Vector3
from queue import PriorityQueue
from Utils.Node import Node, Edge, removeNode
import numpy as np

def smoothPath(startPosition, path, angleTolerance=15):
    if not path:
        return []

    smoothed = [path[0]]
    bundleStart = startPosition
    n = 0
    for i in range(len(path) - 1):
        # vector from bundle start to current and next points
        vec0 = path[i] - bundleStart
        vec1 = path[i + 1] - path[i]

        angle = vec0.angle_to(vec1)
        n +=1
        # when we deviate too far from the current direction, finalize path bundle
        if abs(angle) > angleTolerance:
            smoothed.append(path[i])
            bundleStart = path[i]
            print(n)
            n=0
    
    smoothed.append(path[-1])
    return smoothed

def getAsNodeOnGraph(startPosition: Vector3 , graph: dict[Node, list[Edge]], tmpNodes):
    node = Node(startPosition)
    if node in graph:
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
        if tmpNode in graph:
            graph[tmpNode].append(Edge(node, tmpNode.position.distance_to(node.position)))
            tmpEdge = Edge(tmpNode, node.position.distance_to(tmpNode.position))
            edges.append(tmpEdge)

    graph[node] = edges
    tmpNodes.append(node)
    return node

def aStar(startPosition: Vector3, endPosition: Vector3, graph: dict[Node, list[Edge]], heuristic):
    tmpNodes = []
    startNode = getAsNodeOnGraph(startPosition, graph, tmpNodes)
    targetNode = getAsNodeOnGraph(endPosition, graph, tmpNodes)
    # distances is for storing the shortest distance to node
    distances: dict[Node, float] = {startNode: 0.0}
    open_nodes = PriorityQueue()
    # random is for tie-breaking distances random
    open_nodes.put(
        (
            heuristic(startPosition, endPosition),
            np.random.rand(),
            startNode,
        )
    )

    # incomming nodes is for storing the shortest path between nodes
    incomming_nodes = {}
    
    while open_nodes.not_empty:
        # we only really need the next node
        _, r, currentNode = open_nodes.get()
        # if the next node is the target node the path has been set
        if currentNode == targetNode:
            # backtrak to reconstruct path
            path = []
            while currentNode != startNode:
                path.insert(0, currentNode.position)
                currentNode = incomming_nodes[currentNode]
            
            for node in tmpNodes:
                removeNode(node, graph)
            return smoothPath(startPosition,path)
        
        for edge in graph[currentNode]:
            cost = edge.cost
            new_distance = distances[currentNode] + cost

            if edge.node not in graph:
                print(f'Error node not in graph {edge.node.position}, start Node: {startNode.position}')
                continue
            if edge.node not in distances or new_distance < distances[edge.node]:
                distances[edge.node] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(
                    Vector3(edge.node.position), Vector3(endPosition)
                )
                incomming_nodes[edge.node] = currentNode
                open_nodes.put((predicted_total, np.random.rand(), edge.node))


    return [startPosition]


def slopeAnglePercentage(distance: float, height0: float, height1: float) -> float:
    deltaHeight = height0 - height1
    return distance / np.sqrt(distance * distance + deltaHeight * deltaHeight)
