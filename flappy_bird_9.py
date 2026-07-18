import pygame
import sys
import random
import os
import numpy as np
 
# ---------- Setup ----------
pygame.init()
pygame.mixer.init()
 
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
 
HIGH_SCORE_FILE = "high_score.txt"
 
 
# ---------- High score persistence ----------
 
def load_high_score():
    """Read the saved high score from disk, or 0 if the file doesn't exist yet."""
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except (ValueError, OSError):
            return 0
    return 0
 
 
def save_high_score(value):
    """Write the high score to disk so it persists next time you play."""
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        pass  # if saving fails, just skip it rather than crashing the game
 
 
# ---------- Sound generation ----------
 
def make_tone(frequency, duration_ms, volume=0.3, sample_rate=44100):
    n_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n_samples, False)
    wave = np.sin(frequency * t * 2 * np.pi)
    fade_len = min(500, n_samples)
    fade = np.linspace(1, 0, fade_len)
    wave[-fade_len:] *= fade
    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack([audio, audio])
    return pygame.sndarray.make_sound(stereo)
 
 
def make_sweep(start_freq, end_freq, duration_ms, volume=0.3, sample_rate=44100):
    n_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, n_samples, False)
    freqs = np.linspace(start_freq, end_freq, n_samples)
    wave = np.sin(np.cumsum(freqs) * 2 * np.pi / sample_rate)
    fade_len = min(500, n_samples)
    fade = np.linspace(1, 0, fade_len)
    wave[-fade_len:] *= fade
    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack([audio, audio])
    return pygame.sndarray.make_sound(stereo)
 
 
flap_sound = make_sweep(300, 500, 80, volume=0.2)
score_sound = make_tone(800, 120, volume=0.25)
crash_sound = make_sweep(400, 100, 300, volume=0.3)
 
 
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
high_score = load_high_score()  # <-- loaded once at startup
state = "start"  # "start" | "playing" | "game_over"
 
 
# ---------- Game logic helpers ----------
 
def make_pipe():
    min_top = 50
    max_top = HEIGHT - ground_height - pipe_gap - 50
    top_height = random.randint(min_top, max_top)
    return {"x": WIDTH, "top_height": top_height, "scored": False}
 
 
def get_bird_rect():
    return pygame.Rect(
        bird_x - bird_radius, bird_y - bird_radius,
        bird_radius * 2, bird_radius * 2
    )
 
 
def get_pipe_rects(pipe):
    top_rect = pygame.Rect(pipe["x"], 0, pipe_width, pipe["top_height"])
    bottom_y = pipe["top_height"] + pipe_gap
    bottom_rect = pygame.Rect(
        pipe["x"], bottom_y, pipe_width, HEIGHT - bottom_y - ground_height
    )
    return top_rect, bottom_rect
 
 
def check_collision(bird_rect):
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
    global bird_y, velocity, pipes, frame_count, score, state
    bird_y = HEIGHT // 2
    velocity = 0
    pipes = []
    frame_count = 0
    score = 0
    state = "playing"
 
 
def update_playing_state():
    global frame_count, velocity, bird_y, score, state, high_score
 
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
            score_sound.play()
 
    pipes[:] = [p for p in pipes if p["x"] + pipe_width > 0]
 
    if check_collision(get_bird_rect()):
        state = "game_over"
        crash_sound.play()
        if score > high_score:
            high_score = score
            save_high_score(high_score)  # <-- persist immediately on new record
 
 
def get_bird_angle():
    angle = -velocity * 4
    return max(-30, min(angle, 90))
 
 
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
    size = bird_radius * 2 + 4
    bird_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = size // 2
    pygame.draw.circle(bird_surface, BIRD_COLOR, (center, center), bird_radius)
    pygame.draw.circle(bird_surface, BIRD_OUTLINE, (center, center), bird_radius, 2)
 
    angle = get_bird_angle()
    rotated = pygame.transform.rotate(bird_surface, angle)
    rotated_rect = rotated.get_rect(center=(bird_x, int(bird_y)))
    screen.blit(rotated, rotated_rect)
 
 
def draw_score():
    score_text = big_font.render(str(score), True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(score_text, score_rect)
 
 
def draw_start_screen():
    title = big_font.render("Flappy Bird", True, TEXT_COLOR)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    screen.blit(title, title_rect)
 
    prompt = font.render("Press SPACE to start", True, TEXT_COLOR)
    prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(prompt, prompt_rect)
 
    if high_score > 0:
        hs_text = font.render(f"High Score: {high_score}", True, TEXT_COLOR)
        hs_rect = hs_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(hs_text, hs_rect)
 
 
def draw_game_over_screen():
    box_rect = pygame.Rect(0, 0, 280, 140)
    box_rect.center = (WIDTH // 2, HEIGHT // 2)
    pygame.draw.rect(screen, WHITE, box_rect)
    pygame.draw.rect(screen, (0, 0, 0), box_rect, 3)
 
    line1 = font.render(f"Game Over - Score: {score}", True, TEXT_COLOR)
    line2 = font.render(f"High Score: {high_score}", True, TEXT_COLOR)
    line3 = font.render("SPACE to restart", True, TEXT_COLOR)
    line1_rect = line1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
    line2_rect = line2.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    line3_rect = line3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
    screen.blit(line1, line1_rect)
    screen.blit(line2, line2_rect)
    screen.blit(line3, line3_rect)
 
 
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
                flap_sound.play()
            elif state == "game_over":
                reset_game()
 
    if state == "playing":
        update_playing_state()
 
    draw_frame()
    pygame.display.flip()
 
pygame.quit()
sys.exit()
 