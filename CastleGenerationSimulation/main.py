import pygame
import sys
from Level import Level

print("Hello world")
# Initialize pygame
pygame.init()

# Window size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fortify Simulation")

# Define a grass-green color (R, G, B)
GREEN = (34, 139, 34)

lvl = Level().getLevel()
print()
cell_size = 8

def chaosDisplay(lvl):

    for r in range(len(lvl)):
        for c in range(len(lvl[0])):
            lvl
            color = lvl[r][c],lvl[r][c],lvl[r][c]
            rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with green
    screen.fill(GREEN)
    chaosDisplay(lvl)
    #swap buffer
    pygame.display.flip()

# Quit pygame cleanly
pygame.quit()
sys.exit()
