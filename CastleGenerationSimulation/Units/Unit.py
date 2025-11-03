from pygame import Vector2, Vector3
from Level import Level
from Utils.FSM import FSM
from Utils.FSM import State
from Utils.PathFinding import aStar
from Utils.Node import Node, Edge, Graph
from CastleElement import MaterialBlock

class Unit:
    def __init__(
        self,
        graph: Graph,
        level: Level,
        position: Vector2,
        health: int = 100,
        speed: float = 0.2,
        size=0.1,
    ):
        self.health = health
        self.speed = speed
        self.size = size
        self.level = level
        self.ng = graph
        self.position: Vector3 = Vector3(
            position.x, level.getBilinearHeight(position.x, position.y), position.y
        )
        self.path: list[Node] = []
        self.target = None
        self.goal = None
        self.count = 0
        self.initFSM()
        self.nodesToSkip = []

    def step(self):
        #print(self)
        self.fsm.updateState()
        state = self.fsm.getState()
        if state in self.stateMap:
            self.stateMap[state]()
        return True

    def targetGoal(self):
        self.target = self.goal

    # making a finite state machine. This should be overwritten by subclasses
    def initFSM(self):
        fsm = FSM(State.WAIT)

        fsm.addTransition(
            State.MOVETO, State.WAIT, self.notHasPlan, self.planPath, fsm.onExitPrint,
        )
        fsm.addTransition(
            State.MOVETO, State.STOP, self.closeEnough, fsm.onEnterPrint, fsm.onExitPrint,
        )
        fsm.addTransition(
            State.WAIT,
            State.MOVETO,
            self.hasCounted,
            lambda: setattr(self, "count", 4),
            lambda: setattr(self, "count", 0),
        )
        fsm.addTransition(
            State.STOP, State.WAIT,
            self.outOfReach
        )

        self.fsm = fsm
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.PLANPATH : self.planPath,
            State.WAIT : self.wait
            }

    ######################
    # Transitions
    ######################
    def closeEnough(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) < self.size *3
        )

    def outOfReach(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) > self.size *3
        )
    
    def hasPlan(self):
        return (
            not self.path == []
        )
    def notHasPlan(self):
        return not self.hasPlan()
    
    def hasCounted(self):
        return self.count < 1

    ######################
    # Actions
    ######################

    def wait(self):
        self.count -= 1
        print(self.count)
        pass

    def planPath(self):
        if self.target is None:
            return
        self.path = aStar(
                self.position, self.target, self.ng, unit= self,
                costAdjustFunc= self.moveCostAdjust, ignoreNodes=self.nodesToSkip
            )
        print(len(self.path))
        self.fsm.printState()


    def goToTarget(self):
        if self.notHasPlan():
            return

        for node in self.path[:3]:
            if node.unit is not None and node.unit is not self: 
                self.planPath()
                break
                #return
        self.move(self.path[0].position - self.position)
        if self.position.distance_to(self.path[0].position) <= self.size:
            self.path.pop(0)

    def move(self, direction: Vector3):
        direction.normalize()
        newPosition = self.position + direction * self.speed
        # "hit detection"
        node0 = self.ng.getNodeFromPosition(self.position)
        node1 = self.ng.getNodeFromPosition(newPosition)
        #node is none shield

        ###
        # this stuff needs to be exchanged for the most bare bones but workable hit detection ever
        ###
        adjustmentVector = Vector3()
        if node0 is not None and node1 is not None:
            if node0 is not node1:
                node0.unit = None
                node1.unit = self
        
        for x,y in self.level.getImmediateNeighbors(newPosition.x -0.5,self.position.z-0.5):
            #if walking into a castle bit nudge a bit away
            if self.level.castleMap[y][x] is not None:
                tilePosition = Vector3(x+0.5,self.level.getCell(x,y),y+0.5)
                node = self.ng.getNodeFromPosition(newPosition)
                if node is not None:
                    pass
                    #print(node.materialBlock)
                if newPosition.distance_to(tilePosition) < self.size *2:
                    newPosition = self.position + (direction + (self.position - tilePosition).normalize() * 2).normalize() * self.speed

        self.position = newPosition
        """
            #if the nodes are the same keep traveling through
            if node0 == node1:
                return
                self.position = newPosition
            # now we are moving onto a new node
            else:
                #if there is a unit on the node
                if node1.unit is not None and node1.unit is not self:
                    #self.adjustMoveVector(direction, newPosition,node1.position)
                    #print("unit on node") 
                    #self.move(- direction)# *self.speed
                    #self.planPath()
                    #self.path = [node0, self.ng.nodes[(node0.position.x - (node0.position.x - node1.position.x),(node0.position.z - (node0.position.z - node1.position.z) ))]]
                    #self.nodesToSkip =[ #[node0, self.ng.nodes[(node0.position.x - (node0.position.x - node1.position.x),(node0.position.z - (node0.position.z - node1.position.z) ))]]
                    for edge in self.ng.graph[node1]:
                        self.nodesToSkip.append(edge.node)

                    #node1, 
                    #self.ng.nodes[(node1.position.x +1, node1.position.z)],
                    #self.ng.nodes[(node1.position.x, node1.position.z +1)],
                    #self.ng.nodes[(node1.position.x -1, node1.position.z)],
                    #self.ng.nodes[(node1.position.x, node1.position.z-1)],
                    #]
                    
                    self.path = aStar(
                        node0.position, self.target, self.ng, unit= self,
                        costAdjustFunc= self.moveCostAdjust, ignoreNodes=[node1]
                    )
                    self.nodesToSkip = []
                    return
                #if there is a block on the node
                if node1.materialBlock is not None:
                    #self.adjustMoveVector(direction, newPosition, node1.position)
                    return

                    pass

                node0.unit = None
                node1.unit = self
                self.position = newPosition
            """

    

    def adjustMoveVector(self, direction, newPosition, hitPosition):

        if newPosition.distance_to(hitPosition) < self.size *2:
                    newPosition = self.position + (direction + (self.position - hitPosition).normalize()).normalize() * self.speed
        self.position = newPosition
        #newDirection = self.position + (direction + (self.position - hitPosition).normalize())
        
        #self.move(newDirection)

    # Heuristic for a star calculation, this is here because of relevance to individual units movement
    # and how they account for wall pieces, this can be used to accomodate different kinds of behaviour
    def moveCostAdjust(self, node: Node, edge: Edge):
        cost = edge.cost
        cost += self.blockCost(edge.node)
        cost += self.unitCost(node)
        
        #if perpendicular take corners into account
        perp = abs(node.position.x - edge.node.position.x) + abs(node.position.z - edge.node.position.z)
        if perp >= 2:
            node1 = self.ng.nodes[(edge.node.position.x, node.position.z)]
            node2 = self.ng.nodes[(node.position.x, edge.node.position.z)]
            cost += max(self.blockCost(node1), self.blockCost(node2)) + max(self.unitCost(node1) , self.unitCost(node2))
        
        return cost
    
    def blockCost(self, node):
        if node.materialBlock is not None:
            mBlock: MaterialBlock = node.materialBlock
            return mBlock.health
        return 0.

    def unitCost(self, node):
        if node.unit is not None and node.unit is not self:
            #print(f"big cost {node.position}, {edge.node.position}")
            return 800
        return 0.