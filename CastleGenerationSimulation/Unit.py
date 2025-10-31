from pygame import Vector2, Vector3
from Level import Level
from Utils.FSM import FSM
from Utils.FSM import State
from Utils.PathFinding import aStar
from Utils.PathFinding import slopeAnglePercentage
import numpy as np


class Unit:
    def __init__(
        self,
        graph: dict,
        level: Level,
        position: Vector2,
        health: int = 100,
        speed: float = 0.2,
        size=0.5,
        
    ):
        self.health = health
        self.speed = speed
        self.size = size
        self.level = level
        self.ng = graph
        self.position: Vector3 = Vector3(
            position.x, level.getBilinearHeight(position.x, position.y), position.y
        )
        self.path: list[Vector3] = []
        self.target = None
        self.initFSM()

    def step(self):
        self.fsm.updateState()
        state = self.fsm.getState()
        if state in self.stateMap:
            self.stateMap[state]()
        return True

    # yeah I think this might need to go, set target should probably be something else
    def setTarget(self, x, y):
        self.target = Vector3(x, y, self.level.getCell(x, y))

    # making a finite state machine. This should be overwritten by subclasses
    def initFSM(self):
        self.fsm = FSM()

        subsubFSM = FSM()

        subsubFSM.addTransition(State.STOP, self.outOfReach, State.STOP)
        subsubFSM.setState(State.STOP, subsubFSM.onExitPrint)

        subFSM = FSM()
        subFSM.addTransition(subsubFSM, self.outOfReach, subsubFSM)
        subFSM.setState(subsubFSM, subFSM.onExitPrint)

        self.fsm.addTransition(
            State.MOVETO,
            self.closeEnough,
            subFSM,
            self.fsm.onEnterPrint,
            self.fsm.onExitPrint,
        )
        self.fsm.addTransition(
            subFSM,
            self.outOfReach,
            State.MOVETO,
            self.fsm.onEnterPrint,
            self.fsm.onExitPrint,
        )

        self.fsm.setState(State.MOVETO, self.fsm.onExitPrint)

        self.stateMap = {State.MOVETO: self.goToTarget, State.STOP: self.wait}

    ######################
    # Transitions
    ######################
    def closeEnough(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) < self.size
        )

    def outOfReach(self):
        return (
            self.target is not None
            and self.position.distance_to(self.target) > self.size
        )

    ######################
    # Actions
    ######################

    def wait(self):
        pass

    def goToTarget(self):
        if self.target is None:
            return

        if self.path == []:
            self.path = aStar(
                self.position, self.target, self.ng, self.moveHeuristic
            )
            print(len(self.path))

        self.move((self.path[0] - self.position).normalize())
        if self.position.distance_to(self.path[0]) <= self.size:
            self.path.pop(0)

    def move(self, direction: Vector3):
        # project new position in 2d-space
        tmpPosition = self.position + direction * self.speed
        # use billinear height to find the elevation of the projection
        newHeight = self.level.getBilinearHeight(tmpPosition.x, tmpPosition.z)
        # slopeAngle = slopeAnglePercentage(self.speed, self.position.y, newHeight)
        slopeAngle = 1
        # if it is higher than the new position add a bit of incline fatigue slopeangle squared
        """
        if newHeight > self.position.y:
            newPosition = self.position + direction * (
                self.speed * slopeAngle * slopeAngle
            )
            newPosition.y = self.level.getBilinearHeight(newPosition.x, newPosition.z)
            self.position = newPosition
        else:
        """
        newPosition = self.position + direction * self.speed #* slopeAngle
        #newPosition.y = self.level.getBilinearHeight(newPosition.x, newPosition.z)
        self.position = newPosition

    # Heuristic for a star calculation, this is here because of relevance to individual units movement
    """
    def moveHeuristic(self, pos0: Vector3, pos1: Vector3):
        euclidDist = pos0.distance_to(pos1)
        #if pos0.y < pos1.y:
        #    return euclidDist * euclidDist
        return euclidDist
    """

    def moveHeuristic(self, pos0: Vector3, pos1: Vector3):
        dx = pos0.x - pos1.x
        dz = pos0.z - pos1.z
        base = np.sqrt(dx * dx + dz * dz)
        # *soft* uphill penalty, proportional but not squared
        if pos1.y > pos0.y:
            return base * (1 + (pos1.y - pos0.y) * 0.1)
        return base