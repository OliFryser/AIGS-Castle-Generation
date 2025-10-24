import pygame
import sys

print("Hello world")
# Initialize pygame
pygame.init()

# Window size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fortify Simulation")

# Define a grass-green color (R, G, B)
GREEN = (34, 139, 34)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with green
    screen.fill(GREEN)

    pygame.display.flip()

# Quit pygame cleanly
pygame.quit()
sys.exit()
