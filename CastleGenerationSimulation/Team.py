from pygame import Vector2,Vector3
from Units.Unit import Unit
from Units.AxeMan import AxeMan
from Units.Archer import Archer
from CastleElement import ElementType,CastleElement
from Level import Level

class Team:
    def __init__(self, name, level:Level, startPosition: Vector2, executor, enemies: list[Unit] = []) -> None:
        self.name = name
        self.startPosition = startPosition
        self.units: list[Unit] = []
        self.line = 5
        self.level = level
        self.goal: Vector3 = Vector3(5,self.level.getBilinearHeight(5,5),5)
        self.enemies = enemies
        self.executor = executor

    def addAxeman(self):
        #position = self.getNextPosition()
        position = self.getNextCirclePosition()
        self.units.append(AxeMan(self.level, position, self.executor, goal=self.goal, teamName = self.name, teamMates = self.units, enemies = self.enemies))
    
    def addArcher(self):
        position = self.getNextPosition(self.line)
        self.units.append(Archer(self.level, position,self.executor, goal= self.goal, teamName = self.name, teamMates = self.units, enemies = self.enemies))

    def addArchersToTowers(self):
        #n = 0
        for row in self.level.castleMapDuplo:
            for cell in row:
                if cell is not None and cell.elementType is ElementType.TOWER:
                    position = Vector2(cell.row + self.level.scale/2, cell.column + self.level.scale /2)
                    self.units.append(Archer(self.level, position, goal= self.goal, teamName = self.name, teamMates = self.units, enemies = self.enemies))
                    #n += 1
        #print(f"archers {n}")
       
    def getNextPosition(self, plus = 0):
        index = len(self.units) + plus
        if index == 0:
            return self.startPosition
        side = 1 if index % 2 == 0 else -1
        x = self.startPosition.x + ((index % self.line +1)//2) * side
        y = self.startPosition.y + (index//self.line)
        return Vector2(x,y)
    
    def getNextCirclePosition(self):
        scale = self.level.scale
        height = self.level.height
        width = self.level.width
        eightWinds = [
            Vector2(scale,scale),
            Vector2(width/2,scale),
            Vector2(width - scale,scale),
            Vector2(width - scale, height/2 + scale),
            Vector2(width - scale, height - scale),
            Vector2(width/2 + scale,height - scale),
            Vector2(scale,height - scale),
            Vector2(scale, height/2 + scale),
        ]
        position = eightWinds[len(self.units)%8]# + Vector2(0,round(len(self.units)/8))
        return self.getNextPosition2(position)

    def getNextPosition2(self, position):
        index = int(len(self.units)/8)
        if index == 0:
            return position
        side = 1 if index % 2 == 0 else -1
        x = position.x + ((index % self.line +1)//2) * side
        y = position.y + (index//self.line)
        return Vector2(x,y)
    

    def updateGoal(self, position: Vector3):
        self.goal = position
        for unit in self.units:
            unit.goal = position
            unit.targetGoal()

    def setEnemies(self, enemies: list[Unit]):
        self.enemies = enemies
        for unit in self.units:
            unit.enemies = enemies