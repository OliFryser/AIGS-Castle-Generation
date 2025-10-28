from pygame import Vector3
from queue import PriorityQueue
import numpy as np

def aStar(startPosition, endPosition, level, heuristic):
    start_node = (startPosition[0], startPosition[1], startPosition[2])
    immediateNeighbors = level.getImmediateNeighbors(start_node[0],start_node[1])
    targetNeihbors = level.getImmediateNeighbors(endPosition[0],endPosition[1])
    #distances is for storing the shortest distance to node
    distances = {start_node : 0.}
    
    open_nodes = PriorityQueue()
    #counter is for tie-breaking distances random
    open_nodes.put((heuristic(Vector3(start_node), Vector3(endPosition)), np.random.rand(), start_node))

    #incomming nodes is for storing the shortest path between nodes
    incomming_nodes = {}

    neighbors = immediateNeighbors
    while open_nodes.not_empty:
        #we only really need the next node
        _,r, current_node = open_nodes.get()
        #if the next node is the target node the path has been set
        if current_node in targetNeihbors: #current_node == endPosition:
            #bestTargetNode = current_node
            #backtrak to reconstruct path
            path = []
            while current_node not in immediateNeighbors:
                path.insert(0, Vector3(current_node[0],current_node[1], level.getCell(current_node[0], current_node[1])))
                current_node = incomming_nodes[current_node]
            #printNodesList(path)
            path.insert(0, Vector3(current_node[0],current_node[1], level.getCell(current_node[0], current_node[1])))
            return path
        if current_node == start_node:
            neighbors = immediateNeighbors
        else:
            neighbors = level.getNeighbors(current_node[0], current_node[1])
        for neighbor in neighbors:
            
            #the cost is the distance from the current_node to the neighbour
            if current_node == start_node:
                cNode = start_node
            else:
                cNode = (current_node[0], current_node[1], level.getCell(current_node[0], current_node[1]))
            nNode = (neighbor[0], neighbor[1], level.getCell(neighbor[0], neighbor[1]))
            cost = heuristic(Vector3(cNode), Vector3(nNode))

            new_distance = distances[cNode] + cost

            if nNode not in distances or new_distance < distances[nNode]:
                distances[nNode] = new_distance
                #the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(Vector3(nNode), Vector3(endPosition))
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

def slopeAnglePercentage(d, h0, h1):
    dh = h0 - h1
    return 1 /(d / np.sqrt(d*d + dh*dh))

def getBilinearHeight(x:float, y:float, level) -> float:
    x0 = int(np.floor(x))
    y0 = int(np.floor(y))
    x1 = x0 + 1
    y1 = y0 + 1

    #edge guard
    max_y, max_x = level.height, level.width
    x0 = np.clip(x0, 0, max_x - 1)
    x1 = np.clip(x1, 0, max_x - 1)
    y0 = np.clip(y0, 0, max_y - 1)
    y1 = np.clip(y1, 0, max_y - 1)

    tx = x - x0
    ty = y - y0

    return (
        level.getCell(x0,y0)* (1 - tx) * (1 - ty) +
        level.getCell(x1,y0) * tx * (1 - ty) +
        level.getCell(x0,y1) * (1 - tx) * ty +
        level.getCell(x1,y1) * tx * ty
    )

