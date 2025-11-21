from pygame import Vector2,Vector3
from Units.Unit import Unit
from Units.AxeMan import AxeMan

class Team:
    def __init__(self, level, startPosition: Vector2) -> None:
        self.startPosition = startPosition
        self.units: list[Unit] = []
        self.goal: Vector3|None = None
        self.line = 5
        self.level = level

    def addAxeman(self):
        position = self.getNextPosition()
        self.units.append(AxeMan(self.level, position, goal=self.goal))
    
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