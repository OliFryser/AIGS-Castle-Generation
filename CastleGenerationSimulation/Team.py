from pygame import Vector2,Vector3
from Units.Unit import Unit
from Units.AxeMan import AxeMan
from Level import Level

class Team:
    def __init__(self, name, level:Level, startPosition: Vector2) -> None:
        self.name = name
        self.startPosition = startPosition
        self.units: list[Unit] = []
        self.line = 5
        self.level = level
        self.goal: Vector3 = Vector3(5,self.level.getBilinearHeight(5,5),5)

    def addAxeman(self):
        position = self.getNextPosition()
        self.units.append(AxeMan(self.level, position, goal=self.goal, teamName = self.name, teamMates = self.units))
    
    def getNextPosition(self):
        index = len(self.units)
        if index == 0:
            return self.startPosition
        side = 1 if index % 2 == 0 else -1
        x = self.startPosition.x + ((index % self.line +1)//2) * side
        y = self.startPosition.y + (index//self.line)
        return Vector2(x,y)
    
    def updateGoal(self, position: Vector3):
        self.goal = position
        for unit in self.units:
            unit.goal = position
            unit.targetGoal()