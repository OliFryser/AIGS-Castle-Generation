from pygame import Vector3
from queue import PriorityQueue
import numpy as np

from Level import Level


def aStar(startPosition: Vector3, endPosition: Vector3, level: Level, heuristic):
    start_node: tuple[float, float, float] = (
        startPosition[0],
        startPosition[1],
        startPosition[2],
    )
    immediateNeighbors: list[tuple[int, int]] = level.getImmediateNeighbors(
        start_node[0], start_node[2]
    )
    targetNeighbors: list[tuple[int, int]] = level.getImmediateNeighbors(
        endPosition[0], endPosition[2]
    )
    # distances is for storing the shortest distance to node
    distances: dict[tuple[float, float, float], float] = {start_node: 0.0}

    open_nodes = PriorityQueue()
    # counter is for tie-breaking distances random
    open_nodes.put(
        (
            heuristic(Vector3(start_node), Vector3(endPosition)),
            np.random.rand(),
            start_node,
        )
    )

    # incomming nodes is for storing the shortest path between nodes
    incomming_nodes = {}

    neighbors = immediateNeighbors
    while open_nodes.not_empty:
        # we only really need the next node
        _, r, current_node = open_nodes.get()
        # if the next node is the target node the path has been set
        if current_node in targetNeighbors:  # current_node == endPosition:
            # bestTargetNode = current_node
            # backtrak to reconstruct path
            path = []
            while current_node not in immediateNeighbors:
                path.insert(
                    0,
                    Vector3(
                        current_node[0] + 0.5,
                        level.getCell(current_node[0], current_node[1]),
                        current_node[1] + 0.5,
                    ),
                )
                current_node = incomming_nodes[current_node]
            path.insert(
                0,
                Vector3(
                    current_node[0] + 0.5,
                    level.getCell(current_node[0], current_node[1]),
                    current_node[1] + 0.5,
                ),
            )
            return path

        if current_node == start_node:
            neighbors = immediateNeighbors
        else:
            neighbors = level.getNeighbors(current_node[0], current_node[1])
        for neighbor in neighbors:
            # the cost is the distance from the current_node to the neighbour
            if current_node == start_node:
                cNode = start_node
            else:
                cNode = (
                    current_node[0],
                    level.getCell(current_node[0], current_node[1]),
                    current_node[1],
                )
            neighborNode = (
                neighbor[0],
                level.getCell(neighbor[0], neighbor[1]),
                neighbor[1],
            )
            cost = heuristic(Vector3(cNode), Vector3(neighborNode))

            new_distance = distances[cNode] + cost

            if neighborNode not in distances or new_distance < distances[neighborNode]:
                distances[neighborNode] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(
                    Vector3(neighborNode), Vector3(endPosition)
                )
                incomming_nodes[neighbor] = current_node
                open_nodes.put((predicted_total, np.random.rand(), neighbor))

    return []


"""
def smoothPath(self, path, angleTolerance = 12):
    currentPos = self.position
    tmpPath = [path[0],path[1]]
    for n in range(len(path) -1 ):
        vec0 = (path[n] - currentPos)
        vec0.z = 0
        vec1 = (path[n+1] - path[n])
        vec1.z = 0
        angle = vec0.angle_to(vec1)
        currentPos = path[n]
        if angle < angleTolerance:
            tmpPath = [path[n+1]]
        else:
            return tmpPath
    return tmpPath
"""


def slopeAnglePercentage(distance: float, height0: float, height1: float) -> float:
    deltaHeight = height0 - height1
    return distance / np.sqrt(distance * distance + deltaHeight * deltaHeight)
