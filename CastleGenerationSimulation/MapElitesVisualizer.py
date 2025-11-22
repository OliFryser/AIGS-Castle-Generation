import os
import pygame

# Disable visual for pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"


class MapElitesVisualizer:
    def __init__(self):
        pygame.init()
