from Level import Level
from InitializationParameters import InitializationParameters
from Unit import Unit


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(initParams.levelFilepath)
        unit = Unit(self.level,(40,40,40))
        unit2 = Unit(self.level,(60,60,60))
        unit.target = unit2.position
        self.units = [unit, unit2]

    def step(self):
        for unit in self.units:
            if unit.position[0] < 1:
                print("exit")
                return False
            if not unit.step():
                return False
        return True
        

    def getState(self):
        pass

    def runSimulation(self):
        pass
