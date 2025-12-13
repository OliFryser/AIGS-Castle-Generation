from pygame import Vector2, Vector3
from Level import Level
from Utils.FSM import FSM
from Utils.FSM import State
from Utils.PathFinding import aStar
from Utils.Node import Node, Edge, Graph
from CastleElement import MaterialType
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import time
import uuid


class Unit:
    def __init__(
        self,
        level: Level,
        position: Vector2,
        executor,
        health: int = 100,
        speed: float = 0.2,
        size =0.1,
        goal = Vector3(0,0,0),
        teamName = "blank",
        teamMates = [],
        enemies = [],
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
        self.path: list[Node]|None = None
        self.target = None
        self.goal: None | Vector3 = goal
        self.count = 0
        self.nodesToSkip = []
        self.fsms: dict[str, FSM] = {}
        self.teamName: str = teamName
        self.teamMates = teamMates
        self.blocked = False
        self.enemies = enemies
        self.attackDamage = 1
        self.attackRange = 1
        self.inMelee = None
        self.attackCoolDown = False
        self.future = None
        self.executor = executor
        self.id = uuid.uuid1()
        #self.navGraph = level.navigationGraph
        #place on grid
        self.nodeGraph.getNodeFromPosition(self.position).unit = self
        self.alive = True

        self.initFSMs()
        self.initFSM()

    def step(self):
        if self.future and self.future.done():
            path = self.future.result()
            #self.path = list(self.nodeGraph.nodes[pos2] for pos2 in path)
            if self.alive:
                self.path = path
            self.future = None
        
        if self.future is not None:
            return

        self.fsm.updateState()
        state = self.fsm.getState()
        #self.fsm.printState()
        if state in self.stateMap:
            self.stateMap[state]()
    
    def takeDamage(self, damage):
        self.health -= damage
        #print(f"take damage {self.health}")
        if self.health < 1:
            self.die()
            return True
        return False

    def die(self):
        #print(f"unit {self} died:")
        self.alive = False
        self.nodeGraph.getNodeFromPosition(self.position).unit = None
        self.nodeGraph = None
        self.level = None
        self.position = None
        self.future = None
        self.executor = None
        self.fsm = None
        self.navGraph = None
        self.path = None
        self.inMelee = None
        if self in self.teamMates:
            self.teamMates.remove(self)
        self.teamMates = None
        

    def targetGoal(self):
        self.target = self.goal

    # making a finite state machine. This should be overwritten by subclasses
    def initFSM(self):
        topFSM = FSM("top", State.WAIT)

        goToGoalFSM = None
        if "goToGoal" in self.fsms.keys():
            goToGoalFSM = self.fsms["goToGoal"]

        if goToGoalFSM is not None:
            topFSM.addTransition(
                state0=State.WAIT,
                state1=goToGoalFSM,
                transition=self.hasCounted,
            )
            topFSM.addTransition(
                state0= goToGoalFSM,
                state1= State.WAIT,
                transition=self.closeEnough,
                onEnter= (print, (f"reached goal team: {self.teamName}",), {})
            )

        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.WAIT : self.wait,
            State.PLANPATH : self.planPath,
            }

        self.fsm = topFSM

    # making general fsms to be used by subclasses
    def initFSMs(self):
        #############################################
        # GoToGoal FSM
        #############################################
        goToGoalFSM = FSM("goToGoal", State.WAIT)

        goToGoalFSM.addTransition(
            State.WAIT, 
            State.MOVETO,
            self.hasCounted,
            onEnter = (self.planPath, (), {}),
            )
        goToGoalFSM.addTransition(
            state0= State.MOVETO,
            state1= State.WAIT,
            transition=self.isBlocked,
            onEnter= (self.setTimer, (5,), {}),
            onExit= (self.unBlock, (), {}), 
        )
        goToGoalFSM.addTransition(
            state0= State.MOVETO,
            state1= State.WAIT,
            transition=self.notHasPlan,
            onEnter= (self.setTimer, (5,), {}),
            onExit= (self.unBlock, (), {}), 
        )
        goToGoalFSM.addTransition(
            state0= State.MOVETO,
            state1= State.WAIT,
            transition=self.closeEnough,
            onEnter= (self.setTimer, (5,), {}),
        )
        
        self.fsms[goToGoalFSM.name] = goToGoalFSM

        #############################################
        # Attack FSM
        #############################################

        attackFSM = FSM("attack", State.WAIT)

        attackFSM.addTransition(
            state0=State.WAIT,
            state1=State.ATTACK,
            transition=self.hasCounted,
        )
        attackFSM.addTransition(
            state0=State.ATTACK,
            state1=State.WAIT,
            transition=self.onAttackCoolDown,
            onEnter= (self.setTimer,(self.attackCoolDownTime,),{})
        )
        attackFSM.addTransition(
            state0=State.WAIT,
            state1=State.ATTACK,
            transition=self.hasCounted,
            onExit= (self.setAttackCooldown, (False,), {})
        )
        self.fsms[attackFSM.name] = attackFSM

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

    def onAttackCoolDown(self):
        return self.attackCoolDown

    def hasPlan(self):
        return not (self.path == [] or self.path is None)

    def notHasPlan(self):
        return not self.hasPlan()

    def hasCounted(self):
        return self.count < 1

    def isBlocked(self):
        if not self.blocked:
            self.count = 10
            return False
        self.count -= 1
        if self.count < 1:
            self.blocked = False
            #print("blocked")
            return True
        return False
    
    def isInMelee(self):
        if self.inMelee is not None:
            #print("in melee")
            return True
        return False
    
    def isNotInMelee(self):
        if self.inMelee is None:
            return True
        if self.inMelee not in self.enemies:
            self.inMelee = None
            return True
        if self.position.distance_to(self.inMelee.position) > self.attackRange + self.size:
            self.inMelee = None
            return True
        return False
    
    def enemyInRange(self):
        for unit in self.enemies:
            if self.position.distance_to(unit.position) < self.attackRange:
                self.targetEnemy = unit
                return True
        return False
    
    def enemyOutOfRange(self):
        if self.targetEnemy is None:
            return True
        if self.targetEnemy not in self.enemies:
            self.targetEnemy = None
            return True
        if self.position.distance_to(self.targetEnemy.position) > self.attackRange:
            self.targetEnemy = None
            return True
        return False

    ##########################
    # on enter / exit
    #####################################
    def setTimer(self, n):
        self.count = n

    def unBlock(self):
        self.blocked = False
    
    def setAttackCooldown(self, boo):
        self.attackCoolDown = boo

    ######################
    # Actions
    ######################

    def meleeAttack(self):
        if self.inMelee is not None and self.position.distance_to(self.inMelee.position) < self.attackRange:
            self.inMelee.inMelee = self
            if self.inMelee.takeDamage(self.attackDamage):
                self.inMelee = None
            self.attackCoolDown = True

    def rangeAttack(self):
        if self.targetEnemy is not None:
            if self.targetEnemy.takeDamage(self.attackDamage):
                self.targetEnemy = None
            self.attackCoolDown = True

    def wait(self):
        self.count -= 1
        #print(self.count)
        pass

    def planPathInner(self, toType = None):
        return aStar(
                self.position, self.target, self.nodeGraph,
                costAdjustFunc= self.moveCostAdjust, ignoreNodes=self.nodesToSkip,
                unit=self,
                budget= self.level.height*2,
                getFirstofType=toType
            )

    def planPath(self, target):
        if self.future is None:
            self.future = self.executor(self.planPathInner, target)
            
    
    def cpu_work(self,n=10_000_000):
        s = 0
        for i in range(n):
            s += i  # CPU-bound, holds GIL
        

    def sleep_work(self,sec=0.05):
        time.sleep(sec)  # releases GIL

    def goToTarget(self):
        if self.notHasPlan():
            return

        self.move(self.path[0].position - self.position)
        if self.position.distance_to(self.path[0].position) <= self.size:
            self.path.pop(0)

    def move(self, direction: Vector3, n =0):
        if n > 8:
            return
        self.blocked = False
        direction.normalize()
        newPosition = self.position + direction * self.speed
        # "hit detection"
        node0 = self.nodeGraph.getNodeFromPosition(self.position)
        node1 = self.nodeGraph.getNodeFromPosition(newPosition)
        # node is none shield

        ###
        # this is naive hit detection
        ###
        #clash with units
        if node0 is not None and node1 is not None and node0 is not node1:
            frontNodes = self.getFrontNodes(direction)
            if node1.unit is not None and node1.unit is not self:
                if node1.unit in self.teamMates:
                    self.blocked = True
                    return
                
            for tnode in frontNodes:
                if tnode.unit is not None and tnode.unit in self.enemies:
                    self.inMelee = tnode.unit
                    return
            #clash with walls
            for tnode in frontNodes:
                if tnode.materialBlock is not None and tnode.materialBlock.blocking:
                    if newPosition.distance_to(tnode.position) < self.size *2:
                        newDirection = (direction + (self.position - tnode.position).normalize()).normalize()
                        self.move(newDirection, n+1)
                        return
                """
                if tnode.unit is not None and tnode.unit is not self:
                    other = tnode.unit
                    print(other, self)
                    return
                    if newPosition.distance_to(other.position) < self.size + other.size:
                        # compute push away from other
                        push = (self.position - other.position).normalize()
                        # combine with intended direction
                        newDirection = (direction + push).normalize()
                        self.move(newDirection, n+1)
                        return
                """

        if node0 is not None and node1 is not None:
            if node0 is not node1 and (node1.materialBlock is None or not node1.materialBlock.blocking):
                node0.clearUnit()
                node1.setUnit(self)

        self.position = newPosition
        
    def getFrontNodes(self, direction):
        node = self.nodeGraph.getNodeFromPosition(self.position)
        (x, y) = node.position2

        dx = int(round(direction.x))
        dy = int(round(direction.z))
        if x+dx > self.level.width or x+dx < 0 or y+dy > self.level.height or y+dy < 0:
            return []
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
            return materialBlock.health #/ (self.blockAttackDamage - materialBlock.damageThreshold) * self.attackCoolDownTime/5
        return 0

    def unitCost(self, node):
        if node.unit is not None and node.unit is not self and node.unit not in self.enemies:
            return 10
        return 0
    
    def getAsData(self):
        return str(self.id)
