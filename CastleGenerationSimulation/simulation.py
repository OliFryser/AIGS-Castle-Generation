from Level import Level
from InitializationParameters import InitializationParameters


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(initParams.levelFilepath)

    def step(self):
        pass

    def getState(self):
        pass

    def runSimulation(self):
        pass
