from __future__ import annotations
from typing import Callable
import pygame


class Button:
    def __init__(
        self,
        position: pygame.Vector2,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        onClick: Callable[[Button], None],
    ):
        self.rect = pygame.Rect(position[0], position[1], width, height)
        self.text = text
        self.font = font
        self.onClick = onClick

        self.baseColor = (70, 130, 180)
        self.hoverColor = (100, 160, 210)
        self.selectedColor = (40, 180, 255)

        self.textColor = (255, 255, 255)
        self.textSurface = self.font.render(self.text, True, self.textColor)
        self.textRect = self.textSurface.get_rect(center=self.rect.center)

        self.isSelected = False

    def render(self, surface):
        mousePos = pygame.mouse.get_pos()
        color = self.baseColor
        if self.isSelected:
            color = self.selectedColor
        elif self.rect.collidepoint(mousePos):
            color = self.hoverColor

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        surface.blit(self.textSurface, self.textRect)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.onClick(self)
