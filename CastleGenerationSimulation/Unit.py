from pygame import Vector3


class Unit:
    def __init__(self, position: Vector3, health: int):
        self.position = position
        self.health = health

        # TODO: Init finite state machine

    def step(self):
        pass
