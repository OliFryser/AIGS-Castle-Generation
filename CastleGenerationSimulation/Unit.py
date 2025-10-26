import numpy as np
from pygame import Vector3
from Level import Level
from queue import PriorityQueue
from FSM import FSM
from FSM import State

class Unit:
    def __init__(self, level: Level, position: Vector3 = Vector3 (10,0,10), health: int = 100, speed: float = 0.2, size = 0.5):
        self.health = health
        self.speed = speed
        self.size = size
        self.level = level
        self.position = Vector3(position[0], position[1],self.getBilinearHeight(position[0],position[1]))
        self.path = []
        self.target = None
        self.initFSM()

        # TODO: clean up, move code

    def step(self):
        self.fsm.updateState()
        state = self.fsm.getState()
        if state in self.stateMap:
            self.stateMap[state]()
        return True
    
    #yeah I think this might need to go, set target should probably be something else
    def setTarget(self,x,y):
        self.target = Vector3(x,y, self.level.getCell(x,y))

    #making a finite state machine. This should be overwritten by subclasses
    def initFSM(self):
        self.fsm = FSM()

        subsubFSM = FSM()

        subsubFSM.addTransition(State.STOP, self.outOfReach, State.STOP)
        subsubFSM.setState(State.STOP, subsubFSM.onExitPrint)
        
        subFSM = FSM()
        subFSM.addTransition(subsubFSM, self.outOfReach, subsubFSM)
        subFSM.setState(subsubFSM, subFSM.onExitPrint)

        self.fsm.addTransition(State.MOVETO, self.closeEnough, subFSM, self.fsm.onEnterPrint, self.fsm.onExitPrint)
        self.fsm.addTransition(subFSM, self.outOfReach, State.MOVETO, self.fsm.onEnterPrint, self.fsm.onExitPrint)
        
        self.fsm.setState(State.MOVETO, self.fsm.onExitPrint)
        
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait
        }


    ######################
    # Transitions
    ######################
    def closeEnough(self):
        return self.target is not None and self.position.distance_to(self.target) < self.size
        
    def outOfReach(self):
        return self.target is not None and self.position.distance_to(self.target) > self.size

    ######################
    # Actions
    ######################

    def wait(self):
        pass
        #print("waiting")

    def goToTarget(self):
        if self.target is not None:
            if self.path == []:
                self.path = self.aStar(self.target, self.moveHeuristic)
                if len(self.path)>1:
                    self.path = self.smoothPath(self.path)
            self.move((self.path[0] - self.position).normalize())
            if self.position.distance_to(self.path[0]) <= self.size:
                self.path.pop(0)

    def move(self, direction: Vector3):
        #project new position in 2d-space
        tmpPosition = self.position + direction * self.speed
        #use billinear height to find the elevation of the projection
        newHeight = self.getBilinearHeight(tmpPosition[0], tmpPosition[1]
                                           )
        slopeAngle = self.slopeAnglePercentage(self.position[2], newHeight)
        #if it is higher than the new position add a bit of incline fatigue slopeangle squared
        if newHeight > self.position[2]:
            newPosition = self.position + direction * (self.speed / (slopeAngle * slopeAngle))
            newPosition[2] = self.getBilinearHeight(newPosition[0],newPosition[1])
            self.position = newPosition
        else:
            newPosition = self.position + direction * (self.speed / slopeAngle)
            newPosition[2] = self.getBilinearHeight(newPosition[0],newPosition[1])
            self.position = newPosition

    #######################
    # These are all candidates for going to util, and perhaps one in level

    #this is a candidate for going to util, could be used for interpolationg between points for smoothing rendering of terrain
    def getBilinearHeight(self, x:float, y:float) -> float:
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        x1 = x0 + 1
        y1 = y0 + 1

        #edge guard
        max_y, max_x = self.level.height, self.level.width
        x0 = np.clip(x0, 0, max_x - 1)
        x1 = np.clip(x1, 0, max_x - 1)
        y0 = np.clip(y0, 0, max_y - 1)
        y1 = np.clip(y1, 0, max_y - 1)

        tx = x - x0
        ty = y - y0

        return (
            self.level.getCell(x0,y0)* (1 - tx) * (1 - ty) +
            self.level.getCell(x1,y0) * tx * (1 - ty) +
            self.level.getCell(x0,y1) * (1 - tx) * ty +
            self.level.getCell(x1,y1) * tx * ty
        )

    #angle percentage calculation
    def slopeAnglePercentage(self, h0, h1):
        dh = h0 - h1
        return 1 /(self.speed / np.sqrt(self.speed*self.speed + dh*dh))
    
    
    def aStar(self, end_node, heuristic):
        start_node = (self.position[0], self.position[1], self.position[2])
        immediateNeighbors = self.getImmediateNeighbors(start_node[0],start_node[1])
        targetNeihbors = self.getImmediateNeighbors(end_node[0],end_node[1])
        #distances is for storing the shortest distance to node
        distances = {start_node : 0.}
        
        open_nodes = PriorityQueue()
        #counter is for tie-breaking distances random
        open_nodes.put((heuristic(start_node, end_node), np.random.rand(), start_node))

        #incomming nodes is for storing the shortest path between nodes
        incomming_nodes = {}

        neighbors = immediateNeighbors
        while open_nodes.not_empty:
            #we only really need the next node
            _,r, current_node = open_nodes.get()
            #if the next node is the target node the path has been set
            if current_node in targetNeihbors: #current_node == end_node:
                #bestTargetNode = current_node
                #backtrak to reconstruct path
                path = []
                while current_node not in immediateNeighbors:
                    path.insert(0, Vector3(current_node[0],current_node[1], self.level.getCell(current_node[0], current_node[1])))
                    current_node = incomming_nodes[current_node]
                #printNodesList(path)
                path.insert(0, Vector3(current_node[0],current_node[1], self.level.getCell(current_node[0], current_node[1])))
                return path
            if current_node == start_node:
                neighbors = immediateNeighbors
            else:
                neighbors = self.getNeighbors(current_node[0], current_node[1])
            for neighbor in neighbors:
                
                #the cost is the distance from the current_node to the neighbour
                if current_node == start_node:
                    cNode = start_node
                else:
                    cNode = (current_node[0], current_node[1], self.level.getCell(current_node[0], current_node[1]))
                nNode = (neighbor[0], neighbor[1], self.level.getCell(neighbor[0], neighbor[1]))
                cost = heuristic(cNode, nNode)

                new_distance = distances[cNode] + cost

                if nNode not in distances or new_distance < distances[nNode]:
                    distances[nNode] = new_distance
                    #the predicted total is where the heuristic is applied
                    predicted_total = new_distance + heuristic(nNode, end_node)
                    incomming_nodes[neighbor] = current_node
                    open_nodes.put((predicted_total, np.random.rand(), neighbor))
            
        return []

    def getNeighbors(self,x,y):
        return [
            (x,y+1),
            (x+1,y+1),
            (x+1,y),
            (x+1,y-1),
            (x,y-1),
            (x-1,y-1),
            (x-1,y),
            (x-1,y-1),
        ]

    def euclidianDistance(self, pos0, pos1):
        p0 = Vector3(pos0[0],pos0[1],pos0[2])
        p1 = Vector3(pos1[0],pos1[1],pos1[2])
        return p0.distance_to(p1)

    def moveHeuristic(self, pos0, pos1):
        euclidDist = self.euclidianDistance(pos0, pos1)
        if pos0[2] < pos1[2]:
            return euclidDist * euclidDist
        return euclidDist

    #This should probably be in level
    def getImmediateNeighbors(self, x,y):
        x0 = int(np.floor(x))
        y0 = int(np.floor(y))
        x1 = x0 + 1
        y1 = y0 + 1
        return [
            (x0,y0),
            (x1,y0),
            (x0,y1),
            (x1,y1)
            ]
    
    def smoothPath(self, path, angleTolerance = 55):
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