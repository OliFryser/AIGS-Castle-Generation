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
    cost: int
    towerRatio: float
    kills: int
    gates: int
    stepCount: int
    towers: int
    eastWestRatio: float
    northSouthRatio: float


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(
            initParams.terrainMap,
            initParams.tileMap,
        )
        self.target = Target(self.level)

    def prepare(self, castleInstructionTree):
        self.level.makeCastle(castleInstructionTree)

        self.attacker = Team(
            name="attacker",
            level=self.level,
            startPosition=Vector2(
                self.level.width / 2,
                self.level.height - 6,
            ),
        )
        self.defender = Team(
            name="defender",
            level=self.level,
            startPosition=Vector2(self.target.position.x, self.target.position.z),
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
        self.kills = 0
        self.stepCount = 0


    def step(self):

        for unit in self.getUnits():
            unit.step()

        while len(self.attacker.units) < self.noAttackers:
                self.kills +=1
                """
                #respawn attackers
                self.attacker.addAxeman()
                """
                # or reduce number of attackers
                self.noAttackers -=1
        self.stepCount += 1
        

    def getUnits(self):
        return self.attacker.units + self.defender.units

    def getState(self):
        state = State(
            blocks=self.level.blockCount,
            area=self.level.protectedArea,
            cost=self.getCost(),
            towerRatio=self.level.towerRatio,
            kills=self.kills,
            gates=self.level.gates,
            stepCount=self.getStepCount(),
            towers=self.getTowerAmount(),
            eastWestRatio=self.level.eastWestRatio,
            northSouthRatio=self.level.northSouthRatio,
        )
        return state

    def runSimulation(self):
        while not self.target.isOccupied():
            
            self.step()
            if self.attacker.units == []:
                #self.stepCount = 2000
                break
            if self.stepCount > 40000:
                self.stepCount = 10000
                break        


    def getMaxBlocks(self):
        return self.level.maxBlocks

    def getMaxArea(self):
        return self.level.maxArea

    def getCost(self):
        return self.level.castleCost

    def getStepCount(self):
        return self.stepCount

    def clearUnits(self):
        for unit in self.getUnits():
            unit.die()

    def reset(self):
        # units might hold on to eachother and dodge the garbage collector along with nodes and level and all that jazz
        self.clearUnits()
        self.level.clearCastle()

    def getTowerAmount(self):
        return self.level.getTowers()

    def sanityCheck(self, spacing = ""):
        m=0
        for node in self.level.nodeGraph.graph.keys():
            if node.unit is not None:
                m +=1
        if len(self.getUnits()) != m:       
            print(spacing + f"    Unit Sanity check failed {m, len(self.getUnits())}")
        print(spacing + f"Unit Sanity check {m, len(self.getUnits())}")