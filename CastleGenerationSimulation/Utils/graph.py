import pygame
from pygame import Vector2
from dataclasses import dataclass
from nodes import Node
from constants import TILEWIDTH, TILEHEIGHT, GREEN, RED, PORTAL


@dataclass
class GraphNode(object):
    position: Vector2


# generates a graph that consists of tile in the graph.
class Graph(object):
    def __init__(self, startNode: Node):
        self.visitedNodes: list[Node] = []
        self.connections: dict[Vector2, list[GraphNode]] = {}

        self.generateGraphForNeighbors(startNode)

    def generateGraphForNeighbors(self, fromNode: Node):
        self.visitedNodes.append(fromNode)
        fromGraphNode = GraphNode(fromNode.position)
        self.connections[fromGraphNode.position] = []

        for direction, neighbor in fromNode.neighbors.items():
            if neighbor is None or direction == PORTAL:
                continue

            neighborNode = GraphNode(neighbor.position)
            self.generateGraphBetweenNodes(fromGraphNode, neighborNode)

            if neighbor not in self.visitedNodes:
                self.generateGraphForNeighbors(neighbor)

    def generateGraphBetweenNodes(self, fromNode: GraphNode, toNode: GraphNode):
        isHorizontal = fromNode.position.y == toNode.position.y

        if isHorizontal:
            minNode = fromNode if fromNode.position.x < toNode.position.x else toNode
            maxNode = fromNode if fromNode.position.x >= toNode.position.x else toNode
            nodesBetween = round(
                (maxNode.position.x - minNode.position.x) / TILEWIDTH - 1
            )
        else:
            minNode = fromNode if fromNode.position.y < toNode.position.y else toNode
            maxNode = fromNode if fromNode.position.y >= toNode.position.y else toNode
            nodesBetween = round(
                (maxNode.position.y - minNode.position.y) / TILEHEIGHT - 1
            )

        previousNode = fromNode
        for i in range(1, nodesBetween + 1):
            if isHorizontal:
                node = GraphNode(
                    Vector2(minNode.position.x + i * TILEWIDTH, minNode.position.y)
                )
            else:
                node = GraphNode(
                    Vector2(minNode.position.x, minNode.position.y + i * TILEHEIGHT)
                )
            self.connections[node.position] = []
            self.connections[node.position].append(previousNode)
            self.connections[previousNode.position].append(node)
            previousNode = node
        if toNode.position not in self.connections:
            self.connections[toNode.position] = []

        self.connections[toNode.position].append(previousNode)
        self.connections[previousNode.position].append(toNode)

    # debug visualization
    def render(self, screen):
        for node, connections in self.connections.items():
            x, y = node.asInt()
            x += 8
            y += 8
            pygame.draw.circle(screen, GREEN, (x, y), 5)

            for connection in connections:
                x2, y2 = connection.position.asInt()
                pygame.draw.line(screen, RED, (x, y), (x2 + 8, y2 + 8), 2)
