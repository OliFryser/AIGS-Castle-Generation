from pygame import Vector2, Vector3
from Level import Level
from Units.Unit import Unit
from Utils.FSM import FSM,State
from Utils.Node import Edge, Node, Graph
from CastleElement import MaterialType
from Utils.PathFinding import aStar

class AxeMan(Unit):
    def __init__(self, *args, health: int = 100, speed: float = 0.5, size=0.3 ,**kwargs):
        super().__init__(*args, health, speed, size, **kwargs)
        self.blockAttackDamage = 20
        self.blockAttackRange = 1
        self.attackDamage = 15
        self.attackRange = 1.5
        self.count = 0
        self.nodeTarget = None
        self.attackCoolDown = False
        self.attackCoolDownTime = 20
        self.initFSMs()
        self.initFSM()
        
    def initFSM(self):
        #####################################################
        # Get standard fsms
        #####################################################
        if "goToGoal" not in self.fsms.keys():
            return
        goToGoalFSM = self.fsms["goToGoal"]
        if "attack" not in self.fsms.keys():
            return
        attackFSM = self.fsms["attack"]
        ######################################################
        #Demolishion FSM
        ######################################################
        demolishFsm = FSM("demolish", goToGoalFSM)

        demolishFsm.addTransition(
            goToGoalFSM, State.DEMOLISH, self.closeEnoughToBlock
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
            goToGoalFSM, demolishFsm, self.foundWallWeakPoint, 
            (self.setNodeTargetAndPath, (), {}), onExit= (self.targetGoal, (), {})
        )
        fsm.addTransition(
            State.WAIT, goToGoalFSM, self.hasCounted,
             (self.planPath, (MaterialType.DOOR,), {}), (self.setTimer, (1,),{}),
        )
        fsm.addTransition(
            demolishFsm, State.WAIT, self.targetBlockDemolished, (self.setTimer, (4,),{})
        )
        fsm.addTransition(
            state0=goToGoalFSM,
            state1=attackFSM,
            transition=self.isInMelee,
        )
        """
        fsm.addTransition(
            state0=goToGoalFSM,
            state1=attackFSM,
            transition=self.enemyInRange,
        )
        """
        fsm.addTransition(
            state0=demolishFsm,
            state1=attackFSM,
            transition=self.isInMelee,
        )
        fsm.addTransition(
            state0=demolishFsm,
            state1=attackFSM,
            transition=self.enemyInRange,
        )
        fsm.addTransition(
            state0=State.WAIT,
            state1=attackFSM,
            transition=self.isInMelee,
        )

        fsm.addTransition(
            state0=attackFSM,
            state1=State.WAIT,
            transition=self.isNotInMelee,
            #onEnter=(print,("out of range",),{})
        )

        self.fsm = fsm
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.WAIT : self.wait,
            State.DEMOLISH : self.strikeWall,
            State.ATTACK : self.meleeAttack,
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

    def targetBlockDemolished(self):
        return self.nodeTarget.materialBlock is None
    
    def onAttackCoolDown(self):
        return self.attackCoolDown
    
    ################
    # Enter /exit
    ###########################


    #three/four functions, some might be redundant
    
    def setNodeTargetAndPath(self):
        node = self.path[0]
        self.nodeTarget = node
        self.target = node.position
        self.path = [node]

    def setTargetBlock(self, node):
        self.nodeTarget = node
    
    def setPath(self, path):
        self.path = path

    def setTarget(self, position):
        self.target = position

    def setAttackCooldown(self, boo):
        self.attackCoolDown = boo

    #Action!
    def strikeWall(self):
        block = self.nodeTarget
        if block is not None and self.position.distance_to(block.position) < self.size + self.blockAttackRange +0.6:
            materialBlock = block.materialBlock
            if materialBlock is not None:
                materialBlock.hit(self.blockAttackDamage)
                self.attackCoolDown = True
    
    #this should maybe be somewhere else and handled on a different level
    # it removes the material block from the node, and removes the block from the 
    def destroyCastleElement(self, node: Node):
        node.materialBlock = None
        self.level.castleMap[int(node.position.z - 0.5)][int(node.position.x - 0.5)] = None
        self.nodeTarget = None

    def planPath(self, toType = MaterialType.DOOR):
        self.path = aStar(
                self.position, self.target, self.nodeGraph,
                costAdjustFunc= self.moveCostAdjust2, 
                ignoreNodes=self.nodesToSkip,
                unit=self,
                budget= self.level.height*2,
                getFirstofType=toType
            )

    def moveCostAdjust2(self, node: Node, edge: Edge):
        cost = edge.cost
        if edge.node.unit is not None and edge.node.unit is not self and edge.node.unit in self.teamMates:
            return cost + 10
        return cost
        