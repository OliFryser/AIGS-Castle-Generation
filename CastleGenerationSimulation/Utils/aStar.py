# Modified from "Refactored A*" from Jakob Ehlers

import math
from queue import PriorityQueue
from graph import Graph, Vector2


# this calculates pyhtogoras for two nodes, it's used as heuristic for astar
def euclidianDistanceHeuristic(node0: Vector2, node1: Vector2):
    aSquared = (node1.x - node0.x) ** 2
    bSquared = (node1.y - node0.y) ** 2
    return math.sqrt(aSquared + bSquared)


# Used for a possibly better representation for the node system
def manhattenDistanceHeuristic(startNode: Vector2, endNode: Vector2) -> float:
    return abs(startNode.x - endNode.x) + abs(startNode.y - endNode.y)


# Inspiration from lecture slides. Graph representation is implicit in nodes
def getPathToPosition(
    start_node: Vector2,
    end_node: Vector2,
    graph: Graph,
    heuristic=euclidianDistanceHeuristic,
):
    start_node = getPositionInGraph(start_node, graph)
    end_node = getPositionInGraph(end_node, graph)

    assert start_node in graph.connections
    assert end_node in graph.connections
    # distances is for storing the shortest distance to node
    distances = {start_node: 0.0}

    # incomming nodes is for storing the shortest path between nodes
    incomming_nodes: dict[Vector2, Vector2] = {}

    open_nodes = PriorityQueue()
    open_nodes.put((heuristic(start_node, end_node), start_node))

    closed_nodes = set()

    while open_nodes.not_empty:
        _, current_node = open_nodes.get()
        closed_nodes.add(current_node)
        # Backtrack and reconstruct path
        if current_node == end_node:
            # backtrak to reconstruct path
            path: list[Vector2] = []
            while current_node is not start_node:
                path.insert(0, current_node)
                current_node = incomming_nodes[current_node]
            return path

        for neighbor in graph.connections[current_node]:
            if neighbor.position in closed_nodes:
                continue

            if neighbor.position not in distances:
                distances[neighbor.position] = float("inf")

            # the cost is always the same between nodes
            cost: float = 1

            new_distance: float = distances[current_node] + cost

            if new_distance < distances[neighbor.position]:
                distances[neighbor.position] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total: float = new_distance + heuristic(
                    neighbor.position, end_node
                )
                incomming_nodes[neighbor.position] = current_node
                open_nodes.put((predicted_total, neighbor.position))
    # no path found
    return []


# get the position snapped to the graph
def getPositionInGraph(position, graph):
    position = roundToNearest8(position)
    position = bumpBy8(position, graph)
    return position


# looks messy, but necessary, since each node can be either 24 pixels OR 16 pixels apart, and we use position to index them
def bumpBy8(position, graph):
    if position not in graph.connections:
        bumpedX = Vector2(position.x + 8, position.y)
        bumpedY = Vector2(position.x, position.y + 8)

        reverseBumpedX = Vector2(position.x - 8, position.y)
        reverseBumpedY = Vector2(position.x, position.y - 8)

        if bumpedX in graph.connections:
            position = bumpedX
        elif bumpedY in graph.connections:
            position = bumpedY
        elif reverseBumpedX in graph.connections:
            position = reverseBumpedX
        elif reverseBumpedY in graph.connections:
            position = reverseBumpedY
    return position


# round the position to the nearest multiple of 8
def roundToNearest8(position: Vector2):
    return Vector2((round(position.x / 8) * 8), (round(position.y / 8) * 8))
