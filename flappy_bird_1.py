import pygame
import sys



pygame.init()
 
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Day 1")
clock = pygame.time.Clock()
FPS = 60
 
# Colors
SKY_BLUE = (113, 197, 207)
BIRD_COLOR = (255, 200, 0)
GROUND_COLOR = (222, 184, 135)
 
# ---------- Bird setup ----------
bird_x = WIDTH // 4
bird_y = HEIGHT // 2
bird_radius = 15
 
velocity = 0          # how fast the bird is moving vertically
gravity = 0.5          # how much velocity increases each frame (pulls bird down)
jump_strength = -8     # negative = upward on screen (y increases downward)
 
ground_height = 50
 
# ---------- Game loop ----------
running = True
while running:
    clock.tick(FPS)  # limits the loop to run FPS times per second
 
    # --- Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                velocity = jump_strength  # jump!
 
    # --- Update bird physics ---
    velocity += gravity
    bird_y += velocity
 
    # Stop the bird at the ground
    if bird_y + bird_radius > HEIGHT - ground_height:
        bird_y = HEIGHT - ground_height - bird_radius
        velocity = 0
 
    # Stop the bird at the top of the screen
    if bird_y - bird_radius < 0:
        bird_y = bird_radius
        velocity = 0
 
    # --- Draw everything ---
    screen.fill(SKY_BLUE)
 
    # Ground
    pygame.draw.rect(
        screen, GROUND_COLOR,
        (0, HEIGHT - ground_height, WIDTH, ground_height)
    )
 
    # Bird
    pygame.draw.circle(screen, BIRD_COLOR, (bird_x, int(bird_y)), bird_radius)
 
    pygame.display.flip()  # update the screen with everything drawn
 
pygame.quit()
sys.exit()

