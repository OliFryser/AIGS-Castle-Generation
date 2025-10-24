from Level import Level
from InitializationParameters import InitializationParameters
from Unit import Unit


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(initParams.levelFilepath)
        self.units = [Unit()]

    def step(self):
        for unit in self.units:
            unit.step()
        

    def getState(self):
        pass

    def runSimulation(self):
        pass
