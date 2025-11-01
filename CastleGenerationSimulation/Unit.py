from pygame import Vector2, Vector3
from Level import Level
from Utils.FSM import FSM
from Utils.FSM import State
from Utils.PathFinding import aStar
from Utils.PathFinding import slopeAnglePercentage
from Utils.Node import Node, Edge
from CastleElement import MaterialBlock
import numpy as np


class Unit:
    def __init__(
        self,
        graph: dict,
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
        self.path: list[Vector3] = []
        self.target = None
        self.count = 0
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
        """
        goToTargetFSM = FSM(State.PLANPATH)
        goToTargetFSM.addTransition(State.PLANPATH, self.hasPlan, State.MOVETO)
        goToTargetFSM.addTransition(State.MOVETO, self.closeEnough, State.STOP)
        """

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
        pass

    def planPath(self):
        if self.target is None:
            return
        self.path = aStar(
                self.position, self.target, self.ng, costAdjustFunc= self.moveCostAdjust
            )
        print(len(self.path))

    def goToTarget(self):
        if self.notHasPlan():
            return
        self.move(self.path[0] - self.position)
        if self.position.distance_to(self.path[0]) <= self.size:
            self.path.pop(0)

    def move(self, direction: Vector3):
        direction.normalize
        newPosition = self.position + direction * self.speed
        for x,y in self.level.getImmediateNeighbors(newPosition.x -0.5,self.position.z-0.5):
            #if walking into a castle bit nudge a bit away
            if self.level.castleMap[y][x] is not None:
                tilePosition = Vector3(x+0.5,self.level.getCell(x,y),y+0.5)
                if newPosition.distance_to(tilePosition) < self.size:
                    newPosition = self.position + (direction + (self.position - tilePosition).normalize()).normalize() * self.speed

        self.position = newPosition
    
    # Heuristic for a star calculation, this is here because of relevance to individual units movement
    # and how they account for wall pieces, this can be used to accomodate different kinds of behaviour
    def moveCostAdjust(self, node: Node, edge: Edge):
        cost = edge.cost
        if node.materialBlock is None:
            return cost
        mBlock = node.materialBlock
        return cost + mBlock.health