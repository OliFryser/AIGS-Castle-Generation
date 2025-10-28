from pygame import Vector3
from Target import Target
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
        self.target = Target(
            Vector3(self.level.width / 2, self.level.height / 2, self.level.height / 2)
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
