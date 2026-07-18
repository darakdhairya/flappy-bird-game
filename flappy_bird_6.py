import pygame
import sys
import random
 
# ---------- Setup ----------
pygame.init()
 
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 48)
 
# Colors
SKY_BLUE = (113, 197, 207)
BIRD_COLOR = (255, 200, 0)
BIRD_OUTLINE = (200, 140, 0)
GROUND_COLOR = (222, 184, 135)
GROUND_LINE = (190, 150, 100)
PIPE_COLOR = (60, 160, 60)
PIPE_OUTLINE = (30, 110, 30)
TEXT_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
CLOUD_COLOR = (240, 250, 250)
 
# Bird
bird_x = WIDTH // 4
bird_y = HEIGHT // 2
bird_radius = 15
velocity = 0
gravity = 0.5
jump_strength = -8
 
ground_height = 50
 
# Pipes
pipe_width = 60
pipe_gap = 150
pipe_speed = 3
pipe_spawn_interval = 90
pipes = []
 
# Clouds (decorative only)
clouds = [
    {"x": 50, "y": 80, "size": 30},
    {"x": 200, "y": 130, "size": 20},
    {"x": 320, "y": 60, "size": 25},
]
 
frame_count = 0
score = 0
state = "start"  # "start" | "playing" | "game_over"
 
 
# ---------- Game logic helpers ----------
 
def make_pipe():
    """Create a new pipe just off the right edge, with a random gap height."""
    min_top = 50
    max_top = HEIGHT - ground_height - pipe_gap - 50
    top_height = random.randint(min_top, max_top)
    return {"x": WIDTH, "top_height": top_height, "scored": False}
 
 
def get_bird_rect():
    """Bounding box used for collision checks."""
    return pygame.Rect(
        bird_x - bird_radius, bird_y - bird_radius,
        bird_radius * 2, bird_radius * 2
    )
 
 
def get_pipe_rects(pipe):
    """Return (top_rect, bottom_rect) for a given pipe dict."""
    top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["top_height"])
    bottom_y = pipe["top_height"] + pipe_gap
    bottom_rect = pygame.Rect(
        pipe["x"], bottom_y, pipe_width, HEIGHT - bottom_y - ground_height
    )
    return top_rect, bottom_rect
 
 
def check_collision(bird_rect):
    """True if the bird has hit the ground, ceiling, or any pipe."""
    if bird_rect.bottom >= HEIGHT - ground_height:
        return True
    if bird_rect.top <= 0:
        return True
    for pipe in pipes:
        top_rect, bottom_rect = get_pipe_rects(pipe)
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True
    return False
 
 
def reset_game():
    """Reset all state for a fresh run and switch to 'playing'."""
    global bird_y, velocity, pipes, frame_count, score, state
    bird_y = HEIGHT // 2
    velocity = 0
    pipes = []
    frame_count = 0
    score = 0
    state = "playing"
 
 
def update_playing_state():
    """Advance physics, pipes, and scoring by one frame. Only called while playing."""
    global frame_count, velocity, bird_y, score, state
 
    frame_count += 1
 
    if frame_count % pipe_spawn_interval == 0:
        pipes.append(make_pipe())
 
    velocity += gravity
    bird_y += velocity
 
    for pipe in pipes:
        pipe["x"] -= pipe_speed
        if not pipe["scored"] and pipe["x"] + pipe_width < bird_x:
            score += 1
            pipe["scored"] = True
 
    pipes[:] = [p for p in pipes if p["x"] + pipe_width > 0]
 
    if check_collision(get_bird_rect()):
        state = "game_over"
 
 
# ---------- Drawing helpers ----------
 
def draw_cloud(x, y, size):
    pygame.draw.circle(screen, CLOUD_COLOR, (x, y), size)
    pygame.draw.circle(screen, CLOUD_COLOR, (x + size, y + 10), int(size * 0.8))
    pygame.draw.circle(screen, CLOUD_COLOR, (x - size, y + 10), int(size * 0.8))
 
 
def draw_background():
    screen.fill(SKY_BLUE)
    for cloud in clouds:
        draw_cloud(cloud["x"], cloud["y"], cloud["size"])
 
 
def draw_pipes():
    for pipe in pipes:
        top_rect, bottom_rect = get_pipe_rects(pipe)
        pygame.draw.rect(screen, PIPE_COLOR, top_rect)
        pygame.draw.rect(screen, PIPE_OUTLINE, top_rect, 3)
        pygame.draw.rect(screen, PIPE_COLOR, bottom_rect)
        pygame.draw.rect(screen, PIPE_OUTLINE, bottom_rect, 3)
 
 
def draw_ground():
    pygame.draw.rect(
        screen, GROUND_COLOR,
        (0, HEIGHT - ground_height, WIDTH, ground_height)
    )
    pygame.draw.line(
        screen, GROUND_LINE,
        (0, HEIGHT - ground_height), (WIDTH, HEIGHT - ground_height), 4
    )
 
 
def draw_bird():
    pygame.draw.circle(screen, BIRD_COLOR, (bird_x, int(bird_y)), bird_radius)
    pygame.draw.circle(screen, BIRD_OUTLINE, (bird_x, int(bird_y)), bird_radius, 2)
 
 
def draw_score():
    score_text = big_font.render(str(score), True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(score_text, score_rect)
 
 
def draw_start_screen():
    title = big_font.render("Flappy Bird", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(title, title_rect)
 
    prompt = font.render("Press SPACE to start", True, TEXT_COLOR)
    prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(prompt, prompt_rect)
 
 
def draw_game_over_screen():
    box_rect = pygame.Rect(0, 0, 280, 110)
    box_rect.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, WHITE, box_rect)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, 3)
 
    line1 = font.render(f"Game Over - Score: {score}", True, TEXT_COLOR)
    line2 = font.render("SPACE to restart", True, TEXT_COLOR)
    line1_rect = line1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    line2_rect = line2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(line1, line1_rect)
    screen.blit(line2, line2_rect)
 
 
def draw_frame():
    draw_background()
    if state in ("playing", "game_over"):
        draw_pipes()
    draw_ground()
    if state in ("playing", "game_over"):
        draw_bird()
    if state == "playing":
        draw_score()
    if state == "start":
        draw_start_screen()
    elif state == "game_over":
        draw_game_over_screen()
 
 
# ---------- Main game loop ----------
 
running = True
while running:
    clock.tick(FPS)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if state == "start":
                reset_game()
            elif state == "playing":
                velocity = jump_strength
            elif state == "game_over":
                reset_game()
 
    if state == "playing":
        update_playing_state()
 
    draw_frame()
    pygame.display.flip()
 
pygame.quit()
sys.exit()