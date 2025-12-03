import pygame


class IntSlider:
    def __init__(
        self, x, y, sliderWidth, minValue, maxValue, startValue, title="", font=None
    ):
        self.rect = pygame.Rect(x, y, sliderWidth - 15, 6)
        self.minValue = minValue
        self.maxValue = maxValue
        self.value = int(startValue)

        self.title = title
        self.font = font or pygame.font.SysFont(None, 24)

        self.valueTextPadding = 10
        sampleText = str(maxValue)
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
            mouse_x = event.pos[0]
            mouse_x = max(self.rect.left, min(mouse_x, self.rect.right))

            t = (mouse_x - self.rect.left) / self.rect.width
            rawVal = self.minValue + t * (self.maxValue - self.minValue)

            self.value = int(round(rawVal))
            self.value = max(self.minValue, min(self.value, self.maxValue))

    def _handleRect(self):
        t = (self.value - self.minValue) / (self.maxValue - self.minValue)
        handle_x = self.rect.left + t * self.rect.width

        return pygame.Rect(
            int(handle_x - self.handle_radius),
            int(self.rect.centery - self.handle_radius),
            self.handle_radius * 2,
            self.handle_radius * 2,
        )

    def render(self, surface):
        # --- Draw title ---
        if self.title:
            title_surf = self.font.render(self.title, True, (255, 255, 255))
            surface.blit(title_surf, (self.rect.left, self.rect.top - 25))

        # --- Draw slider track ---
        pygame.draw.rect(surface, self.trackColor, self.rect, border_radius=3)

        # --- Draw handle ---
        color = self.selectedColor if self.dragging else self.handle_color
        pygame.draw.circle(
            surface, color, self._handleRect().center, self.handle_radius
        )

        # --- Draw value text to the right ---
        value_surf = self.font.render(str(self.value), True, (255, 255, 255))
        value_x = self.rect.right + self.valueTextPadding
        value_y = self.rect.centery - value_surf.get_height() // 2
        surface.blit(value_surf, (value_x, value_y))
