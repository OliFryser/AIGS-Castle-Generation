from dataclasses import dataclass
from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Team import Team
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

@dataclass
class State:
    blocks: int
    area: int
    cost: int
    towerRatio: float
    kills: int
    gates: int
    fitness: int


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(
            initParams.terrainMap,
            initParams.castleInstructionTree,
            initParams.tileMap,
        )
        self.executor = ThreadPoolExecutor(max_workers=4)#ProcessPoolExecutor()

        self.attacker = Team(
            name="attacker",
            level=self.level,
            startPosition=Vector2(
                self.level.width / 2,
                self.level.height - 6,
            ),
            executor=self.executor
        )
        self.target = Target(self.level)
        self.defender = Team(
            name="defeder",
            level=self.level,
            startPosition=Vector2(self.target.position.x, self.target.position.z),
            executor= self.executor,
            enemies=self.attacker.units,
        )
        self.attacker.setEnemies(self.defender.units)
        self.target.enemies = self.attacker.units
        self.defender.addArchersToTowers()
        for n in range(8 + len(self.defender.units)):
            self.attacker.addAxeman()


        self.attacker.updateGoal(self.target.position)
        self.defender.updateGoal(self.target.position)
        self.target.team = self.defender.units
        self.noAttackers = len(self.attacker.units)

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
        state = State(
            blocks= self.level.blockCount,
            area= self.level.protectedArea,
            cost= self.getCost(),
            towerRatio= self.level.towerRatio,
            kills= self.kills,
            gates= self.level.gates,
            fitness=self.getFitness(),
            )
        return state

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
        self.kills = - (len(self.attacker.units) - self.noAttackers)
        # units might hold on to eachother and dodge the garbage collector along with nodes and level and all that jazz
        self.clearUnits()

    def clearUnits(self):
        for unit in self.getUnits():
            unit.die()

    def getMaxBlocks(self):
        return self.level.maxBlocks

    def getMaxArea(self):
        return self.level.maxArea
    
    def getCost(self):
        return self.level.castleCost
    
    def getFitness(self):
        """
        castleCost = self.level.castleCost
        castleBudget = 100
        overBudget = 0
        if castleCost > castleBudget:
            overBudget = (castleCost - castleBudget) * 20
            #overBudget = overBudget*overBudget
            #print(overBudget)
        return self.stepCount - overBudget
        """
        return self.stepCount
    
    def shutdown(self):
        self.executor.shutdown(wait=False)