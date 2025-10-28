from pygame import Vector3
from Target import Target
from Level import Level
from InitializationParameters import InitializationParameters
from Unit import Unit


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(initParams.levelFilepath)
        self.units = [Unit()]
        self.target = Target(
            Vector3(self.level.width / 2, self.level.height / 2, self.level.height / 2)
        )

    def step(self):
        for unit in self.units:
            unit.step()

    def getState(self):
        pass

    def runSimulation(self):
        pass
