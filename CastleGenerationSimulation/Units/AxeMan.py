from pygame import Vector2
from Level import Level
from Units.Unit import Unit
from Utils.FSM import FSM,State
from Utils.Node import Node, Graph

class AxeMan(Unit):
    def __init__(self, graph: Graph, level: Level, position: Vector2, health: int = 100, speed: float = 0.1, size=0.3):
        super().__init__(graph, level, position, health, speed, size)
        self.blockAttackDamage = 10
        self.blockAttackRange = 0.8
        self.count = 0
        self.targetBlock = None
        self.attackCoolDown = False
        self.attackCoolDownTime = 50
        self.initFSM()

    def initFSM(self):
        ######################################################
        #Demolishion FSM
        ######################################################
        demolishFsm = FSM("demolish", State.MOVETO)

        demolishFsm.addTransition(
            State.MOVETO, State.DEMOLISH, self.closeEnoughToBlock
        )
        demolishFsm.addTransition(
            State.DEMOLISH, State.WAIT, self.onAttackCoolDown, onEnter= (self.setTimer,(self.attackCoolDownTime,),{})
        )
        demolishFsm.addTransition(
            State.WAIT, State.DEMOLISH, self.hasCounted, onExit= (self.setAttackCooldown, (False,), {})
        )

        #######################################################
        #Top FSM
        #######################################################
        fsm = FSM("top",State.WAIT)

        fsm.addTransition(
            State.MOVETO, demolishFsm, self.foundWallWeakPoint, 
            (self.setNodeTargetAndPath, (), {}), onExit= (self.targetGoal, (), {})
        )
        fsm.addTransition(
            State.MOVETO, State.STOP, self.closeEnough
        )
        fsm.addTransition(
            State.MOVETO, State.WAIT, self.notHasPlan,(self.setTimer,(1,),{})
        )
        fsm.addTransition(
            State.WAIT, State.MOVETO, self.hasCounted,
             (self.planPath, (), {}), (self.setTimer, (1,),{}),
        )
        fsm.addTransition(
            State.STOP, State.WAIT,
            self.outOfReach
        )
        fsm.addTransition(
            demolishFsm, State.WAIT, self.nodeTargetDestroyed, (self.setTimer, (4,),{})
        )

        self.fsm = fsm
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.PLANPATH : self.planPath,
            State.WAIT : self.wait,
            State.DEMOLISH : self.strikeWall
            }
        
    #Transition conditions
    def foundWallWeakPoint(self):
        if self.path == []:
            return False
        return (
            self.path[0].materialBlock is not None and self.path[0].materialBlock.blocking
        )
    
    def closeEnoughToBlock(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) < self.size + self.blockAttackRange
        )

    def nodeTargetDestroyed(self):
        return self.targetBlock is None
    
    def onAttackCoolDown(self):
        return self.attackCoolDown
    
    ################
    # Enter /exit
    ###########################


    #three/four functions, some might be redundant
    
    def setNodeTargetAndPath(self):
        node = self.path[0]
        self.targetBlock = node
        self.target = node.position
        self.path = [node]

    def setTargetBlock(self, node):
        self.targetBlock = node
    
    def setPath(self, path):
        self.path = path

    def setTarget(self, position):
        self.target = position

    def setAttackCooldown(self, boo):
        self.attackCoolDown = boo

    #Action!
    def strikeWall(self):
        block = self.targetBlock
        if block is not None and self.position.distance_to(block.position) < self.size + self.blockAttackRange +0.6:
            materialBlock = block.materialBlock
            if materialBlock is not None:
                materialBlock.health -= self.blockAttackDamage - materialBlock.damageThreshold
                self.attackCoolDown = True
                if materialBlock.health < 0:   
                    self.destroyCastleElement(block)
                    self.targetBlock = None
    
    #this should maybe be somewhere else and handled on a different level
    # it removes the material block from the node, and removes the block from the 
    def destroyCastleElement(self, node: Node):
        node.materialBlock = None
        self.level.castleMap[int(node.position.z - 0.5)][int(node.position.x - 0.5)] = None
        self.targetBlock = None