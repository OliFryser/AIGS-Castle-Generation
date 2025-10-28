from Level import Level
from InitializationParameters import InitializationParameters
from Unit import Unit


class Simulation:
    def __init__(self, initParams: InitializationParameters):
        self.level = Level(initParams.levelFilepath)
        #these are test things
        unit = Unit(self.level,(40,40,40))
        unit0 = Unit(self.level,(10,10,50))
        unit1 = Unit(self.level,(30,20,10))
        unit2 = Unit(self.level,(60,60,60))
        unit.target = unit2.position
        unit0.target = unit2.position
        unit1.target = unit2.position
        self.units = [unit, unit0, unit1, unit2]

    def step(self):
        i = 0
        for unit in self.units:
            if not unit.step():
                i+= 1                
            if i > 2:
                return False
        return True
        

    def getState(self):
        pass

    def runSimulation(self):
        pass
