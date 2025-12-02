from dataclasses import dataclass
from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Team import Team


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

        self.attacker = Team(
            "attacker",
            self.level,
            Vector2(
                self.level.width / 2,
                self.level.height - 6,
            ),
        )
        self.target = Target(self.level)
        self.defender = Team(
            "defeder",
            self.level,
            Vector2(self.target.position.x, self.target.position.z),
            self.attacker.units,
        )
        self.attacker.setEnemies(self.defender.units)
        self.target.enemies = self.attacker.units
        self.defender.addArchersToTowers()
        for n in range(8 + len(self.defender.units)):
            self.attacker.addAxeman()


        self.attacker.updateGoal(self.target.position)
        self.defender.updateGoal(self.target.position)
        self.target.team = self.defender.units

    def step(self):
        for unit in self.getUnits():
            unit.step()
        # Node unit sanity check, should not be run, it is expensive
        """
        n = 0
        for node in self.level.nodeGraph.graph.keys():
            if node.unit is not None:
                n +=1
        if len(self.getUnits()) > n:       
            print(f"Sanity check failed {n, len(self.getUnits())}")
        """

    def getUnits(self):
        return self.attacker.units + self.defender.units

    def getState(self):
        return State(self.level.blockCount, self.level.protectedArea, self.getFitness())

    def runSimulation(self):
        self.stepCount = 0
        while not self.target.isOccupied():
            self.step()
            self.stepCount += 1
            if self.attacker.units == []:
                self.stepCount = 20000
                break
            if self.stepCount > 20000:
                print("step Break")
                break
        # units might hold on to eachother and dodge the garbage collector along with nodes and level and all that jazz
        self.clearUnits()

    def clearUnits(self):
        for unit in self.getUnits():
            unit.die()

    def getMaxBlocks(self):
        return self.level.maxBlocks

    def getMaxArea(self):
        return self.level.maxArea
    
    def getFitness(self):
        castleCost = self.level.castleCost
        castleBudget = 100
        overBudget = 0
        if castleCost > castleBudget:
            overBudget = (castleCost - castleBudget) * 20
            #overBudget = overBudget*overBudget
            #print(overBudget)
        return self.stepCount - overBudget
