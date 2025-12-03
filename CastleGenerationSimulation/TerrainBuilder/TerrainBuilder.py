from enum import IntEnum
import math

import pygame

from TerrainBuilder.IntSlider import IntSlider
from TerrainBuilder.Button import Button
from TerrainBuilder.Slider import Slider
from TerrainBuilder.TerrainBuilderRenderer import TerrainBuilderRenderer
from TerrainMap import TerrainMap


class TerrainTool(IntEnum):
    TERRAIN = 0
    WATER = 1
    PATH = 2


class TerrainBuilder:
    def __init__(self, cfg, terrainMap: TerrainMap):
        pygame.init()

        # used by path
        self.castleGridSize = 5

        self.brushPreviewColor = (40, 210, 255, 80)
        self.leftMouseButtonHeld = False
        self.rightMouseButtonHeld = False
        self.currentTool: TerrainTool = TerrainTool.TERRAIN
        self.levelFilepath: str = cfg.levelFilepath
        self.terrainMap: TerrainMap = terrainMap
        self.resolution = cfg.resolution
        self.statusBarOffset = 50
        self.screen = pygame.display.set_mode(
            (
                terrainMap.width * self.resolution,
                self.statusBarOffset + terrainMap.height * self.resolution,
            )
        )
        self.terrainBuilderRenderer = TerrainBuilderRenderer(
            self.terrainMap, cfg.resolution, self.statusBarOffset
        )

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)

        buttonFont = pygame.font.Font(None, 24)
        buttonHeight = 30
        toolButtonWidth = 80
        self.toolButtons = [
            Button(
                pygame.Vector2(10, 10),
                toolButtonWidth,
                buttonHeight,
                "Terrain",
                buttonFont,
                lambda b: self.onToolButtonClick(TerrainTool.TERRAIN, b),
            ),
            Button(
                pygame.Vector2(10 * 2 + toolButtonWidth, 10),
                toolButtonWidth,
                buttonHeight,
                "Water",
                buttonFont,
                lambda b: self.onToolButtonClick(TerrainTool.WATER, b),
            ),
            Button(
                pygame.Vector2(10 * 3 + toolButtonWidth * 2, 10),
                toolButtonWidth,
                buttonHeight,
                "Path",
                buttonFont,
                lambda b: self.onToolButtonClick(TerrainTool.PATH, b),
            ),
        ]

        sliderWidth = 180
        currentX = 10 * 4 + toolButtonWidth * 3
        self.brushSizeSlider = IntSlider(
            x=currentX,
            y=30,
            sliderWidth=sliderWidth,
            minValue=1,
            maxValue=30,
            startValue=5,
            title="Brush size",
        )
        currentX += self.brushSizeSlider.totalWidth

        self.strengthSlider = Slider(
            x=currentX,
            y=30,
            sliderWidth=sliderWidth,
            minValue=0,
            maxValue=5,
            startValue=1,
            title="Brush strength",
        )

        currentX += self.strengthSlider.totalWidth

        self.saveButton = Button(
            position=pygame.Vector2(currentX, 10),
            width=50,
            height=buttonHeight,
            text="Save",
            font=buttonFont,
            onClick=lambda b: self.onSaveButtonClick(b),
        )

        self.toolButtons[0].isSelected = True
        self.currentTool = TerrainTool.TERRAIN

    def onSaveButtonClick(self, _):
        self.terrainMap.saveToFile(self.levelFilepath)

    def onToolButtonClick(self, tool: TerrainTool, button: Button):
        self.currentTool = tool

        for but in self.toolButtons:
            but.isSelected = False

        button.isSelected = True

    def run(self):
        self.running = True

        while self.running:
            self.processEvents()
            self.update()
            self.render()
            self.clock.tick(60)

    def processEvents(self):
        self.mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.leftMouseButtonHeld = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.leftMouseButtonHeld = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.rightMouseButtonHeld = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.rightMouseButtonHeld = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                targetPosX, targetPosY = self.mousePos
                targetPosX = targetPosX // self.resolution
                targetPosY = (targetPosY - self.statusBarOffset) // self.resolution
                self.terrainMap.target = (targetPosX, targetPosY)

            for b in self.toolButtons:
                b.handleEvent(event)

            self.saveButton.handleEvent(event)

            self.brushSizeSlider.handleEvent(event)
            self.strengthSlider.handleEvent(event)

    def update(self):
        if self.withinScreenTerrainMap(self.mousePos):
            if self.leftMouseButtonHeld:
                if self.currentTool == TerrainTool.TERRAIN:
                    self.modifyTerrain(increase=True)
                elif self.currentTool == TerrainTool.WATER:
                    self.modifyWater(add=True)
                else:
                    self.modifyPath(add=True)
            elif self.rightMouseButtonHeld:
                if self.currentTool == TerrainTool.TERRAIN:
                    self.modifyTerrain(increase=False)
                elif self.currentTool == TerrainTool.WATER:
                    self.modifyWater(add=False)
                else:
                    self.modifyPath(add=False)

        self.strength: float = self.strengthSlider.value
        self.brushSize: int = self.brushSizeSlider.value

    def render(self):
        self.screen.fill((30, 30, 48))
        self.terrainBuilderRenderer.render(self.screen)
        for b in self.toolButtons:
            b.render(self.screen)
        self.brushSizeSlider.render(self.screen)
        self.strengthSlider.render(self.screen)
        if self.currentTool == TerrainTool.PATH:
            self.renderSquareBrushPreview(self.screen)
        else:
            self.renderBrushPreview(self.screen)
        self.saveButton.render(self.screen)

        # self.showFPS()
        pygame.display.flip()

    def showFPS(self):
        fps = self.clock.get_fps()
        fpsText = self.font.render(f"{fps:.4f} FPS", True, (255, 255, 255))

        # Position: top-right corner
        textRect = fpsText.get_rect(topright=(self.screen.get_width() - 10, 10))
        self.screen.blit(fpsText, textRect)

    def renderSquareBrushPreview(self, screen):
        screenSpaceBrushSize = self.castleGridSize * self.resolution

        brushPreviewSurface = pygame.Surface(
            (
                screenSpaceBrushSize * 2,
                screenSpaceBrushSize * 2,
            ),
            pygame.SRCALPHA,
        )

        rect = pygame.rect.Rect(0, 0, screenSpaceBrushSize, screenSpaceBrushSize)

        pygame.draw.rect(
            brushPreviewSurface,
            self.brushPreviewColor,
            rect,
        )

        x = (self.mousePos[0] // screenSpaceBrushSize) * screenSpaceBrushSize
        y = (
            self.mousePos[1] // screenSpaceBrushSize
        ) * screenSpaceBrushSize + screenSpaceBrushSize // 2

        screen.blit(
            brushPreviewSurface,
            (x, y),
        )

    def renderBrushPreview(self, screen):
        screenSpaceBrushSize = self.brushSize * self.resolution

        brushPreviewSurface = pygame.Surface(
            (
                screenSpaceBrushSize * 2,
                screenSpaceBrushSize * 2,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            brushPreviewSurface,
            self.brushPreviewColor,
            (screenSpaceBrushSize, screenSpaceBrushSize),
            screenSpaceBrushSize,
        )

        screen.blit(
            brushPreviewSurface,
            (
                self.mousePos[0] - screenSpaceBrushSize,
                self.mousePos[1] - screenSpaceBrushSize,
            ),
        )

    def modifyTerrain(self, increase: bool):
        self.terrainBuilderRenderer.terrainMapCached = False
        mouseX, mouseY = self.mousePos
        mouseX, mouseY = self.screenToGridSpace(mouseX, mouseY)

        cellX = mouseX // self.resolution
        cellY = mouseY // self.resolution

        radius = max(self.brushSize, 1)
        radiusSquared = radius * radius

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = cellX + dx
                y = cellY + dy

                if not self.withinLevelBounds(x, y):
                    continue

                # Distance squared from center
                distSq = dx * dx + dy * dy

                # Skip anything outside circle
                if distSq > radiusSquared:
                    continue

                # Compute normalized distance (0 at center → 1 at edge)
                if distSq == 0:
                    distNorm = 0.0
                else:
                    distNorm = math.sqrt(distSq) / radius

                falloff = 1.0 - distNorm  # linear falloff

                strength = falloff * self.strength  # scale with tool strength

                if strength <= 0:
                    continue

                if increase:
                    self.terrainMap.increaseHeight(x, y, strength)
                else:
                    self.terrainMap.decreaseHeight(x, y, strength)

    def modifyWater(self, add: bool):
        self.terrainBuilderRenderer.terrainMapCached = False
        mouseX, mouseY = self.mousePos
        mouseX, mouseY = self.screenToGridSpace(mouseX, mouseY)

        cellX = mouseX // self.resolution
        cellY = mouseY // self.resolution

        radius = max(self.brushSize, 1)
        radiusSquared = radius * radius

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = cellX + dx
                y = cellY + dy

                if not self.withinLevelBounds(x, y):
                    continue

                # Distance squared from center
                distSq = dx * dx + dy * dy

                # Skip anything outside circle
                if distSq > radiusSquared:
                    continue

                if add:
                    self.terrainMap.addWater(x, y)
                else:
                    self.terrainMap.removeWater(x, y)

    def modifyPath(self, add: bool):
        self.terrainBuilderRenderer.terrainMapCached = False
        mouseX, mouseY = self.mousePos
        mouseX, mouseY = self.screenToGridSpace(mouseX, mouseY)

        cellX = mouseX // self.resolution
        cellY = mouseY // self.resolution

        brushSize = self.castleGridSize // 2
        cellX = (cellX // self.castleGridSize) * self.castleGridSize + brushSize
        cellY = (cellY // self.castleGridSize) * self.castleGridSize + brushSize

        if add:
            self.terrainMap.addPath(cellX, cellY)
        else:
            self.terrainMap.removePath(cellX, cellY)

    def withinLevelBounds(self, x, y):
        return 0 <= x < self.terrainMap.width and 0 <= y < self.terrainMap.height

    def withinScreenTerrainMap(self, pos: tuple[int, int]) -> bool:
        return (
            0 <= pos[0] < self.terrainMap.width * self.resolution
            and 0 + self.statusBarOffset
            <= pos[1]
            < self.terrainMap.height * self.resolution + self.statusBarOffset
        )

    def screenToGridSpace(self, x, y) -> tuple[int, int]:
        return (x, y - self.statusBarOffset)
