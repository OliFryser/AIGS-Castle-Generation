import pygame


class Slider:
    def __init__(
        self, x, y, sliderWidth, minValue, maxValue, startValue, title="", font=None
    ):
        self.rect = pygame.Rect(x, y, sliderWidth - 15, 6)  # track
        self.minValue = minValue
        self.maxValue = maxValue
        self.value = startValue

        self.title = title
        self.font = font or pygame.font.SysFont(None, 24)

        self.valueTextPadding = 10
        sampleText = f"{self.maxValue}:.1f"
        textWidth, textHeight = self.font.size(sampleText)

        self.totalWidth = sliderWidth + textWidth + self.valueTextPadding

        # Handle
        self.handle_radius = 10
        self.handle_color = (200, 200, 200)
        self.trackColor = (100, 100, 120)
        self.selectedColor = (40, 180, 255)

        self.dragging = False

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._handleRect().collidepoint(event.pos):
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            # convert mouse x to slider value
            mouse_x = event.pos[0]
            mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))
            t = (mouse_x - self.rect.left) / self.rect.width
            self.value = self.minValue + t * (self.maxValue - self.minValue)

    def _handleRect(self):
        """Returns the handle's rect for collision detection."""
        t = (self.value - self.minValue) / (self.maxValue - self.minValue)
        handle_x = self.rect.left + t * self.rect.width
        return pygame.Rect(
            handle_x - self.handle_radius,
            self.rect.centery - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2,
        )

    def render(self, surface):
        if self.title:
            title_surf = self.font.render(self.title, True, (255, 255, 255))
            surface.blit(title_surf, (self.rect.left, self.rect.top - 25))

        pygame.draw.rect(surface, self.trackColor, self.rect, border_radius=3)

        color = self.selectedColor if self.dragging else self.handle_color
        pygame.draw.circle(
            surface, color, self._handleRect().center, self.handle_radius
        )

        value_surf = self.font.render(f"{self.value:.1f}", True, (255, 255, 255))
        value_x = self.rect.right + self.valueTextPadding
        value_y = self.rect.centery - value_surf.get_height() // 2
        surface.blit(value_surf, (value_x, value_y))
