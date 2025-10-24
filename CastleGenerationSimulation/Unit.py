from pygame import Vector3


class Unit:
    def __init__(self, position: Vector3 = Vector3 (200,200,200), health: int = 100, speed: float = 0.05):
        self.position = position
        self.health = health
        self.speed = speed
        # TODO: Init finite state machine

    def step(self):
        self.move(Vector3(1,1,0))
        pass
    
    def move(self, direction: Vector3):
        self.position = self.position + direction * self.speed