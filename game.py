import pygame
import sys
import random
import os
import json

# ===== SETTINGS =====
DEFAULT_SETTINGS = {
    "width": 600,
    "height": 400,
    "cell_size": 20,
    "fps": 6,
    "level_file": "levels/level1.txt"
}

def load_settings():
    try:
        with open("settings.json", "r") as f:
            user_settings = json.load(f)
            return {**DEFAULT_SETTINGS, **user_settings}
    except:
        return DEFAULT_SETTINGS

settings = load_settings()
WIDTH = settings["width"]
HEIGHT = settings["height"]
CELL_SIZE = settings["cell_size"]
FPS = settings["fps"]
LEVEL_FILE = settings.get("level_file", "levels/level1.txt")

ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

# ===== COLORS =====
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# ===== INIT =====
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Levels")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

def draw_block(color, pos):
    x, y = pos
    pygame.draw.rect(screen, color, [x, y, CELL_SIZE, CELL_SIZE])

def draw_text(text, size, color, x, y, center=True):
    font = pygame.font.SysFont("arial", size)
    label = font.render(text, True, color)
    rect = label.get_rect()
    rect.center = (x, y) if center else (x, y)
    screen.blit(label, rect)

def main_menu():
    while True:
        screen.fill(BLACK)
        draw_text("SNAKE GAME", 40, GREEN, WIDTH // 2, HEIGHT // 4)
        draw_text("Press ENTER to Start", 24, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text("ESC to Quit | Level: " + os.path.basename(LEVEL_FILE), 20, GRAY, WIDTH // 2, HEIGHT - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

def game_over_screen(score, high_score):
    while True:
        screen.fill(BLACK)
        draw_text("GAME OVER", 40, RED, WIDTH // 2, HEIGHT // 4)
        draw_text(f"Your Score: {score}", 24, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
        draw_text(f"High Score: {high_score}", 24, GREEN, WIDTH // 2, HEIGHT // 2 + 10)
        draw_text("Press ENTER to Return to Menu", 20, GRAY, WIDTH // 2, HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def load_level(path):
    obstacles = []
    start = (CELL_SIZE, CELL_SIZE)
    food = None

    if not os.path.exists(path):
        return start, food, obstacles

    with open(path) as f:
        lines = f.readlines()

    for row, line in enumerate(lines):
        for col, char in enumerate(line.strip()):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            if char == "#":
                obstacles.append((x, y))
            elif char == "S":
                start = (x, y)
            elif char == "F":
                food = (x, y)

    return start, food, obstacles

def random_free_position(snake, obstacles):
    while True:
        x = random.randrange(0, WIDTH, CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        pos = (x, y)
        if pos not in snake and pos not in obstacles:
            return pos

def main_game():
    start_pos, fixed_food, obstacles = load_level(LEVEL_FILE)
    snake = [start_pos]
    direction = (CELL_SIZE, 0)
    score = 0
    high_score = load_high_score()
    food = fixed_food if fixed_food else random_free_position(snake, obstacles)

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(high_score)
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction[1] == 0:
                    direction = (0, -CELL_SIZE)
                elif event.key == pygame.K_DOWN and direction[1] == 0:
                    direction = (0, CELL_SIZE)
                elif event.key == pygame.K_LEFT and direction[0] == 0:
                    direction = (-CELL_SIZE, 0)
                elif event.key == pygame.K_RIGHT and direction[0] == 0:
                    direction = (CELL_SIZE, 0)

        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake.insert(0, head)

        if (
            head in snake[1:] or
            not (0 <= head[0] < WIDTH and 0 <= head[1] < HEIGHT) or
            head in obstacles
        ):
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            game_over_screen(score, high_score)
            return

        if head == food:
            score += 1
            food = random_free_position(snake, obstacles)
        else:
            snake.pop()

        screen.fill(BLACK)

        for obs in obstacles:
            draw_block(GRAY, obs)
        for segment in snake:
            draw_block(GREEN, segment)
        draw_block(RED, food)

        draw_text(f"Score: {score}", 20, WHITE, 10, 10, center=False)
        draw_text(f"High: {high_score}", 20, GRAY, WIDTH - 120, 10, center=False)

        pygame.display.update()

# Loop
while True:
    main_menu()
    main_game()
