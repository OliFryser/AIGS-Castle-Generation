from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Units.AxeMan import AxeMan
from Utils.Node import createNodeGraph
from Utils.Node import createHexNodeGrap


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(
            initParams.levelFilepath, initParams.castleGenerationFilepath, initParams.castleTilesFilepath
        )   
        self.units = []
        self.updateNodeGraph()
        # these are test things
        unit = AxeMan(self.ng,self.level, Vector2(20, 80))
        unit0 = AxeMan(self.ng,self.level, Vector2(10, 50))
        unit1 = AxeMan(self.ng,self.level, Vector2(30, 10))
        self.target = Target(
            self.level, Vector2(self.level.width / 2 +1.5, self.level.height / 2 +2.5)
        )
        
        self.units = [unit, unit0, unit1]
        for u in self.units:
            u.goal = self.target.position
            u.targetGoal()

    def step(self):
        for unit in self.units:
            unit.step()

    def getState(self):
        pass

    def runSimulation(self):
        pass

    def updateNodeGraph(self):
        graphs = [
            createNodeGraph(self.level),
            #createHexNodeGrap(self.level),
        ]
        self.ng = graphs[0]
        for unit in self.units:
            unit.ng = self.ng
