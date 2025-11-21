from pygame import Vector2, Vector3
from Level import Level
from Utils.FSM import FSM
from Utils.FSM import State
from Utils.PathFinding import aStar
from Utils.Node import Node, Edge, Graph
from CastleElement import MaterialType


class Unit:
    def __init__(
        self,
        level: Level,
        position: Vector2,
        health: int = 100,
        speed: float = 0.2,
        size=0.1,
        goal= None
    ):
        self.health = health
        self.speed = speed
        self.size = size
        self.blockAttackDamage = 0
        self.blockAttackRange = 0
        self.attackCoolDownTime = 1000

        self.level = level
        self.nodeGraph: Graph = level.nodeGraph
        self.position: Vector3 = Vector3(
            position.x, level.getBilinearHeight(position.x, position.y), position.y
        )
        self.path: list[Node] = []
        self.target = None
        self.goal: None | Vector3 = goal
        self.count = 0
        self.initFSM()
        self.nodesToSkip = []

    def step(self):
        # print(self)
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
            State.MOVETO,
            State.WAIT,
            self.notHasPlan,
            self.planPath,
            fsm.onExitPrint,
        )
        fsm.addTransition(
            State.MOVETO,
            State.STOP,
            self.closeEnough,
            fsm.onEnterPrint,
            fsm.onExitPrint,
        )
        fsm.addTransition(
            State.WAIT,
            State.MOVETO,
            self.hasCounted,
            lambda: setattr(self, "count", 4),
            lambda: setattr(self, "count", 0),
        )
        fsm.addTransition(State.STOP, State.WAIT, self.outOfReach)

        self.fsm = fsm
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.WAIT: self.wait,
        }

    ######################
    # Transition bools
    ######################
    def closeEnough(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) < self.size * 3
        )

    def outOfReach(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) > self.size * 3
        )

    def hasPlan(self):
        return not self.path == []

    def notHasPlan(self):
        return not self.hasPlan()

    def hasCounted(self):
        return self.count < 1

    ##########################
    # on enter / exit
    #####################################
    def setTimer(self, n):
        self.count = n

    ######################
    # Actions
    ######################

    def wait(self):
        self.count -= 1
        # print(self.count)
        pass

    def planPath(self, toType = None):
        if self.target is None:
            return
        self.path = aStar(
                self.position, self.target, self.nodeGraph,
                costAdjustFunc= self.moveCostAdjust, ignoreNodes=self.nodesToSkip,
                unit=self,
                getFirstofType=toType
            )
        #print(len(self.path))
        #self.fsm.printState()


    def goToTarget(self):
        if self.notHasPlan():
            return

        #for avoiding units
        """
        """
        for node in self.path[:1]:
            if node.unit is not None and node.unit is not self:
                self.planPath()
                break
                # return
        if self.path == []:
            return
        self.move(self.path[0].position - self.position)
        if self.position.distance_to(self.path[0].position) <= self.size:
            self.path.pop(0)

    def move(self, direction: Vector3, n =0):
        if n > 4:
            return
        
        direction.normalize()
        newPosition = self.position + direction * self.speed
        # "hit detection"
        node0 = self.nodeGraph.getNodeFromPosition(self.position)
        node1 = self.nodeGraph.getNodeFromPosition(newPosition)
        #node is none shield

        ###
        # this stuff needs to be exchanged for the most bare bones but workable hit detection ever
        ###
        
        frontNodes = self.getFrontNodes(direction)
        for tnode in frontNodes:
            if tnode.unit is not None and tnode.unit is not self:
                other = tnode.unit
                if newPosition.distance_to(other.position) < self.size + other.size:
                    # compute push away from other
                    push = (self.position - other.position).normalize()
                    # combine with intended direction
                    newDirection = (direction + push).normalize()
                    self.move(newDirection, n+1)
                    return
            if tnode.materialBlock is not None and tnode.materialBlock.blocking:
                if newPosition.distance_to(tnode.position) < self.size *2:
                    newDirection = (direction + (self.position - tnode.position).normalize()).normalize()
                    self.move(newDirection, n+1)
                    return

        if node0 is not None and node1 is not None:
            if node0 is not node1 and (node1.materialBlock is None or not node1.materialBlock.blocking):
                node0.unit = None
                node1.unit = self

        self.position = newPosition
        
    def getFrontNodes(self, direction):
        node = self.nodeGraph.getNodeFromPosition(self.position)
        (x, y) = node.position2

        dx = int(round(direction.x))
        dy = int(round(direction.z))
        nodes = [self.nodeGraph.nodes[(x+dx,y+dy)]]
        if abs(dx) + abs(dy) >=2:
            if x+dx >=0 and x+dx <= self.level.width:
                nodes.append(self.nodeGraph.nodes[(x+dx,y)])
            if y+dy >= 0 and y+dy <= self.level.height:
                nodes.append(self.nodeGraph.nodes[(x,y+dy)])
                
        elif dx == 0:
            if y+dy >= 0 and y+dy <= self.level.height:
                if x+1 <= self.level.width:
                    nodes.append(self.nodeGraph.nodes[(x+1, y+dy)])
                if x-1 >= 0:
                    nodes.append(self.nodeGraph.nodes[(x-1, y+dy)])
        
        elif dy == 0:
            if x+dx >=0 and x+dx <= self.level.width:
                if y +1 < self.level.height:
                    nodes.append(self.nodeGraph.nodes[(x+dx, y+1)])
                if y -1 >= 0:
                    nodes.append(self.nodeGraph.nodes[(x+dx, y-1)])

        return nodes

  
    # Heuristic for a-star calculation, this is here because of relevance to individual units movement
    # and how they account for wall pieces, this can be used to accomodate different kinds of behaviour
    def moveCostAdjust(self, node: Node, edge: Edge):
        cost = edge.cost
        cost += self.blockCost(edge.node)
        cost += self.unitCost(node)

        # if perpendicular take corners into account
        perp = abs(node.position.x - edge.node.position.x) + abs(
            node.position.z - edge.node.position.z
        )
        if perp >= 2:
            node1 = self.nodeGraph.nodes[(edge.node.position.x, node.position.z)]
            node2 = self.nodeGraph.nodes[(node.position.x, edge.node.position.z)]
            cost += max(self.blockCost(node1), self.blockCost(node2)) + max(self.unitCost(node1) , self.unitCost(node2))
        
        return cost

    def blockCost(self, node):
        if node.materialBlock is not None and node.materialBlock.blocking:
            materialBlock: MaterialType = node.materialBlock
            if self.blockAttackDamage <=  materialBlock.damageThreshold:
                return 10000
            return materialBlock.health/ (self.blockAttackDamage - materialBlock.damageThreshold) * self.attackCoolDownTime/5
        return 0

    def unitCost(self, node):
        if node.unit is not None and node.unit is not self:
            # print(f"big cost {node.position}, {edge.node.position}")
            return 1400
        return 0
