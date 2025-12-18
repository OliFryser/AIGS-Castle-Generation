from dataclasses import dataclass
from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Team import Team
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from threading import Semaphore


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
            name="defeder",
            level=self.level,
            startPosition=Vector2(self.target.position.x, self.target.position.z),
            enemies=self.attacker.units,
        )
        self.attacker.setEnemies(self.defender.units)
        self.target.enemies = self.attacker.units

        self.defender.addArchersToTowers()
        """
        """
        for n in range(8 + len(self.defender.units)):
            self.attacker.addAxeman()

        self.attacker.updateGoal(self.target.position)
        self.defender.updateGoal(self.target.position)
        self.target.team = self.defender.units
        self.noAttackers = len(self.attacker.units)

    def step(self):
        # step accomodating the threading
        # should be run specifically for the non-rendered runs as it doesn't really matter with the render slow-down
        """
        if self.attackersAreAllPlanning():
            print("all planning")
            return
        """

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
            blocks=self.level.blockCount,
            area=self.level.protectedArea,
            cost=self.getCost(),
            towerRatio=self.level.towerRatio,
            kills=self.kills,
            gates=self.level.gates,
            stepCount=self.getStepCount(),
            towers=self.getTowerAmount(),
        )
        return state

    def runSimulation(self):
        self.stepCount = 0
        n = 0

        self.sanityCheck("start ")

        while not self.target.isOccupied():
            # if all attackers are planning... the game can run "amok" while they are waiting for threads
            # this should make the simulation slightly more deterministic
            if self.attackersAreAllPlanning():
                # print(f"all planning consecutive: {n}")
                n += 1
                # usually pathfinding shouldnt be stuck for more than 10 consecutive steps processor dependant
                if n > 10000:
                    print("no one could find a path")
                    self.stepCount = 0
                    self.kills = -(len(self.attacker.units) - self.noAttackers)
                    return
                continue
            self.step()
            self.stepCount += 1
            n = 0
            if self.attacker.units == []:
                # self.stepCount = 20000
                print("wipeout")
                break
            if self.stepCount > 40000:
                self.stepCount = 10000
                print("step Break")
                break
        self.kills = -(len(self.attacker.units) - self.noAttackers)
        
        self.sanityCheck("end ")

    def attackersAreAllPlanning(self):
        for u in self.attacker.units:
            f = u.future
            if f is None or f.done():
                # this unit is NOT planning
                return False
        return True

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
        self.sanityCheck(" reset ")

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