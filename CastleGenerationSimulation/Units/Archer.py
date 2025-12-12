from pygame import Vector2, Vector3
from Level import Level
from Units.Unit import Unit
from Utils.FSM import FSM,State

class Archer(Unit):
    def __init__(self, *args, health: int = 100, speed: float = 0.2, size=0.3 ,**kwargs):
        super().__init__(*args, health, speed, size, **kwargs)
        self.attackDamage = 8
        self.attackRange = 10
        self.attackCoolDown = False
        self.attackCoolDownTime = 20
        self.targetEnemy = None
        self.initFSMs()
        self.initFSM()

    
    def initFSM(self):
        fsm = FSM("topFSM",State.WAIT)

        if "attack" not in self.fsms.keys():
            return
        attackFSM = self.fsms["attack"]

        fsm.addTransition(
            state0=State.WAIT,
            state1=attackFSM,
            transition=self.enemyInRange
        )
        
        fsm.addTransition(
            state0=attackFSM,
            state1=State.WAIT,
            transition=self.enemyOutOfRange
        )
        
        self.fsm = fsm
        self.stateMap = {
            State.MOVETO: self.goToTarget,
            State.STOP: self.wait,
            State.WAIT : self.wait,
            State.ATTACK : self.rangeAttack,
            }
        pass


    #########################
    # transition
    #########################
    