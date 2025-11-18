from dataclasses import dataclass
from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Units.AxeMan import AxeMan


@dataclass
class State:
    blocks: int
    area: int
    stepCount: int


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(
            initParams.terrainMap,
            initParams.castleInstructionTree,
            initParams.tileMap,
        )
        self.units = []
        # these are test things
        unit = AxeMan(self.level, Vector2(20, 80))
        unit0 = AxeMan(self.level, Vector2(10, 50))
        unit1 = AxeMan(self.level, Vector2(30, 10))
        self.target = Target(self.level)

        self.units = [unit, unit0, unit1]
        for u in self.units:
            u.goal = self.target.position
            u.targetGoal()

    def step(self):
        for unit in self.units:
            unit.step()
        """
        #Node unit sanity check
        n = 0
        for node in self.ng.graph.keys():
            if node.unit is not None:
                n +=1
        print(n)
        """

    def getState(self):
        return State(self.level.castleCost, self.level.protectedArea, self.stepCount)

    def runSimulation(self):
        self.stepCount = 0
        while not self.target.isOccupied():
            self.step()
            self.stepCount += 1
