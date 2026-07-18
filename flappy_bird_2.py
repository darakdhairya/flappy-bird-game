import pygame
import sys
import random
 
# ---------- Setup ----------
pygame.init()
 
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Day 2")
clock = pygame.time.Clock()
FPS = 60
 
# Colors
SKY_BLUE = (113, 197, 207)
BIRD_COLOR = (255, 200, 0)
GROUND_COLOR = (222, 184, 135)
PIPE_COLOR = (60, 160, 60)
 
# ---------- Bird setup ----------
bird_x = WIDTH // 4
bird_y = HEIGHT // 2
bird_radius = 15
 
velocity = 0
gravity = 0.5
jump_strength = -8
 
ground_height = 50
 
# ---------- Pipe setup ----------
pipe_width = 60
pipe_gap = 150          # vertical gap the bird flies through
pipe_speed = 3
pipe_spawn_interval = 90  # frames between new pipes (90 frames = 1.5s at 60 FPS)
 
# Each pipe is a dict: {"x": ..., "top_height": ...}
# top_height = how tall the top pipe is; the gap starts right after it
pipes = []
 
def make_pipe():
    """Create a new pipe with a random gap position."""
    min_top = 50
    max_top = HEIGHT - ground_height - pipe_gap - 50
    top_height = random.randint(min_top, max_top)
    return {"x": WIDTH, "top_height": top_height, "scored": False}
 
frame_count = 0
 
# ---------- Game loop ----------
running = True
while running:
    clock.tick(FPS)
    frame_count += 1
 
    # --- Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                velocity = jump_strength
 
    # --- Spawn new pipes on a timer ---
    if frame_count % pipe_spawn_interval == 0:
        pipes.append(make_pipe())
 
    # --- Update bird physics ---
    velocity += gravity
    bird_y += velocity
 
    if bird_y + bird_radius > HEIGHT - ground_height:
        bird_y = HEIGHT - ground_height - bird_radius
        velocity = 0
 
    if bird_y - bird_radius < 0:
        bird_y = bird_radius
        velocity = 0
 
    # --- Update pipes: move left, remove off-screen ones ---
    for pipe in pipes:
        pipe["x"] -= pipe_speed
 
    # Keep only pipes still visible (or just off the left edge)
    pipes = [p for p in pipes if p["x"] + pipe_width > 0]
 
    # --- Draw everything ---
    screen.fill(SKY_BLUE)
 
    # Pipes
    for pipe in pipes:
        top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["top_height"])
        bottom_y = pipe["top_height"] + pipe_gap
        bottom_rect = pygame.Rect(
            pipe["x"], bottom_y, pipe_width, HEIGHT - bottom_y - ground_height
        )
        pygame.draw.rect(screen, PIPE_COLOR, top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, bottom_rect)
 
    # Ground (drawn after pipes so it sits on top of them at the bottom)
    pygame.draw.rect(
        screen, GROUND_COLOR,
        (0, HEIGHT - ground_height, WIDTH, ground_height)
    )
 
    # Bird
    pygame.draw.circle(screen, BIRD_COLOR, (bird_x, int(bird_y)), bird_radius)
 
    pygame.display.flip()
 
pygame.quit()
sys.exit()