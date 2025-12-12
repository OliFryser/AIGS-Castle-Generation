from queue import PriorityQueue
import numpy as np
import math

def slopeAnglePercentage(distance: float, height0: float, height1: float) -> float:
    deltaHeight = height0 - height1
    return distance / np.sqrt(distance * distance + deltaHeight * deltaHeight)

def getNodeFromPosition2(position: tuple[float,float,float], nodes):
    nodeid = (np.floor(position[0])+0.5, np.floor(position[2]) +0.5)
    if nodeid in nodes:
        return nodes[nodeid]

def distanceCost2(node, edge):
    return edge["cost"]

def euclidianDistance2(node0, node1):
    a = node0["position"]
    b = node1["position"]
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)
    #return np.linalg.norm(node0["position"] - node1["position"])

def aStar2(
    startPosition: tuple[float,float,float],
    targetPosition: tuple[float,float,float],
    nodeGraph,
    heuristic=euclidianDistance2,
    costAdjustFunc=distanceCost2,
    budget=50,
    unit=None,
    getFirstofType=None,
):
    graph = nodeGraph["graph"]
    # pprint(graph.values())
    tmpNodes = []
    startNode = getNodeFromPosition2(startPosition, nodeGraph["nodes"])
    targetNode = getNodeFromPosition2(targetPosition, nodeGraph["nodes"])
    # distances is for storing the shortest distance to node
    distances = {startNode["position2"]: 0.0}

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
    
    print()
    
    while open_nodes.not_empty:
        # we only really need the next node
        _, r, currentNode = open_nodes.get()
        
        # print(currentNode[position],graph[currentNode])
        """
        if (currentNode.unit is not None and currentNode.unit is not unit):
            print(f" unit {currentNode.unit}, {unit}")
            print(f"price {distances[currentNode]}")
        """

        # if the next node is the target node the path has been set
        if distances[currentNode["position2"]] > budget:
            cast =distances[currentNode["position2"]]
            print(f"could not find path within budget {cast, len(distances.keys())}")
            # print(currentNode.unit, currentNode.materialBlock.materialType)
            break

        if currentNode["position2"] == targetNode["position2"] or (
            getFirstofType is not None
            and currentNode["materialBlock"] is not None
            and getFirstofType == currentNode["materialBlock"]["materialType"]
        ):
            """
            """
            cast = distances[currentNode["position2"]]
            print(f"path cost {cast}")

            # backtrak to reconstruct path
            path = []
            while currentNode["position2"] != startNode["position2"]:
                path.insert(0, currentNode["position2"])
                # if currentNode.materialBlock is not None:
                # path = []
                currentNode = incomming_nodes[currentNode["position2"]]

            return path
        #random.shuffle((graph[currentNode]))
        for edge in graph[currentNode["position2"]]:
            # cost is calculated here
            cost = costAdjustFunc(currentNode, edge)
            """
            if cost > 200:
                print(cost)
                #continue
            """

            new_distance = distances[currentNode["position2"]] + cost
            #print(new_distance)

            if edge["node"]["position2"] not in graph:
                print(
                    f"Error node not in graph" #{edge[node]["position"]}, start Node: {startNode["position"]}"
                )
                continue
            if edge["node"]["position2"] not in distances or new_distance < distances[edge["node"]["position2"]]:
                distances[edge["node"]["position2"]] = new_distance
                # the predicted total is where the heuristic is applied
                predicted_total = new_distance + heuristic(edge["node"], targetNode)
                incomming_nodes[edge["node"]["position2"]] = currentNode
                open_nodes.put((predicted_total, np.random.rand(), edge["node"]))

    return []
