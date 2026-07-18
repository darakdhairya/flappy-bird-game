import pygame
import sys
import random
 
# ---------- Setup ----------
pygame.init()
 
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Day 3")
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont(None, 48)
 
# Colors
SKY_BLUE = (113, 197, 207)
BIRD_COLOR = (255, 200, 0)
GROUND_COLOR = (222, 184, 135)
PIPE_COLOR = (60, 160, 60)
TEXT_COLOR = (30, 30, 30)
 
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
pipe_gap = 150
pipe_speed = 3
pipe_spawn_interval = 90
 
pipes = []
 
def make_pipe():
    min_top = 50
    max_top = HEIGHT - ground_height - pipe_gap - 50
    top_height = random.randint(min_top, max_top)
    return {"x": WIDTH, "top_height": top_height}
 
def get_bird_rect():
    """Return a pygame Rect approximating the bird, for collision checks."""
    return pygame.Rect(
        bird_x - bird_radius, bird_y - bird_radius,
        bird_radius * 2, bird_radius * 2
    )
 
def check_collision(bird_rect, pipes):
    """Return True if the bird hits the ground, ceiling, or any pipe."""
    # Ground / ceiling
    if bird_rect.bottom >= HEIGHT - ground_height:
        return True
    if bird_rect.top <= 0:
        return True
 
    # Pipes
    for pipe in pipes:
        top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["top_height"])
        bottom_y = pipe["top_height"] + pipe_gap
        bottom_rect = pygame.Rect(
            pipe["x"], bottom_y, pipe_width, HEIGHT - bottom_y - ground_height
        )
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True
 
    return False
 
frame_count = 0
game_over = False
 
# ---------- Game loop ----------
running = True
while running:
    clock.tick(FPS)
 
    # --- Handle events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    velocity = jump_strength
                else:
                    # Press space after game over to restart
                    bird_y = HEIGHT // 2
                    velocity = 0
                    pipes = []
                    frame_count = 0
                    game_over = False
 
    if not game_over:
        frame_count += 1
 
        # Spawn new pipes on a timer
        if frame_count % pipe_spawn_interval == 0:
            pipes.append(make_pipe())
 
        # Update bird physics
        velocity += gravity
        bird_y += velocity
 
        # Update pipes
        for pipe in pipes:
            pipe["x"] -= pipe_speed
        pipes = [p for p in pipes if p["x"] + pipe_width > 0]
 
        # Check collisions
        bird_rect = get_bird_rect()
        if check_collision(bird_rect, pipes):
            game_over = True
 
    # --- Draw everything ---
    screen.fill(SKY_BLUE)
 
    for pipe in pipes:
        top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["top_height"])
        bottom_y = pipe["top_height"] + pipe_gap
        bottom_rect = pygame.Rect(
            pipe["x"], bottom_y, pipe_width, HEIGHT - bottom_y - ground_height
        )
        pygame.draw.rect(screen, PIPE_COLOR, top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, bottom_rect)
 
    pygame.draw.rect(
        screen, GROUND_COLOR,
        (0, HEIGHT - ground_height, WIDTH, ground_height)
    )
 
    pygame.draw.circle(screen, BIRD_COLOR, (bird_x, int(bird_y)), bird_radius)
 
    if game_over:
        box_rect = pygame.Rect(0, 0, 300, 100)
        box_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(screen, (255, 255, 255), box_rect)  # white background
        pygame.draw.rect(screen, (0, 0, 0), box_rect, 3)     # black border, 3px thick

        line1 = font.render("Game Over", True, TEXT_COLOR)
        line2 = font.render("SPACE to restart", True, TEXT_COLOR)
        line1_rect = line1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        line2_rect = line2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(line1, line1_rect)
        screen.blit(line2, line2_rect)

    pygame.display.flip()
 
pygame.quit()
sys.exit()