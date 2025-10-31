from pygame import Vector2
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Unit import Unit
from Utils.Node import createNodeGraph


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(
            initParams.levelFilepath, initParams.castleGenerationFilepath
        )
        self.units = []
        self.updateNodeGraph()
        # these are test things
        unit = Unit(self.ng,self.level, Vector2(20, 80))
        unit0 = Unit(self.ng,self.level, Vector2(10, 50))
        unit1 = Unit(self.ng,self.level, Vector2(30, 10))
        self.target = Target(
            self.level, Vector2(self.level.width / 2, self.level.height / 2)
        )
        unit.target = self.target.position
        unit0.target = self.target.position
        unit1.target = self.target.position
        self.units = [unit, unit0, unit1]

    def step(self):
        for unit in self.units:
            unit.step()

    def getState(self):
        pass

    def runSimulation(self):
        pass

    def updateNodeGraph(self):
        self.ng = createNodeGraph(self.level)
    
        for unit in self.units:
            unit.ng = self.ng
