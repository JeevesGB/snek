import pygame
import sys
import os
import json
import random

# ====== Load Settings ======
DEFAULT_SETTINGS = {
    "width": 900,
    "height": 600,
    "cell_size": 20,
    "fps": 6,
    "start_level": 1,
    "levels_to_win": 3,
    "food_per_level": 5
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
START_LEVEL = settings["start_level"]
LEVELS_TO_WIN = settings["levels_to_win"]
FOOD_PER_LEVEL = settings["food_per_level"]

ROWS = HEIGHT // CELL_SIZE
COLS = WIDTH // CELL_SIZE

# ====== Load Theme ======
DEFAULT_THEME = {
    "snake": [0, 200, 0],
    "food": [255, 50, 50],
    "obstacle": [120, 120, 120],
    "animated_obstacle": [255, 0, 255],
    "background": [0, 0, 0],
    "text": [255, 255, 255]
}

def load_theme():
    try:
        with open("theme.json", "r") as f:
            user_theme = json.load(f)
            return {**DEFAULT_THEME, **user_theme}
    except:
        return DEFAULT_THEME

theme = load_theme()

# ====== Init ======
pygame.init()
pygame.mixer.init()
death_sound = pygame.mixer.Sound("audio/deathsound.mp3")
food_sound = pygame.mixer.Sound("audio/foodpickup.mp3")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                line = f.read().strip()
                if ":" in line:
                    name, score = line.split(":")
                    return name.strip(), int(score.strip())
            except:
                return "", 0
    return "", 0

def save_high_score(name, score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(f"{name}: {score}")

def draw_block(color, pos):
    pygame.draw.rect(screen, color, [pos[0], pos[1], CELL_SIZE, CELL_SIZE])

def draw_text(text, size, color, x, y, center=True):
    font = pygame.font.SysFont("arial", size)
    label = font.render(text, True, color)
    rect = label.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(label, rect)

def main_menu(high_name, high_score):
    while True:
        screen.fill(theme["background"])
        draw_text("SNAKE GAME", 40, theme["snake"], WIDTH // 2, HEIGHT // 4)
        draw_text("Press ENTER to Start", 24, theme["text"], WIDTH // 2, HEIGHT // 2)
        draw_text(f"High Score: {high_name} - {high_score}", 20, theme["text"], WIDTH // 2, HEIGHT - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return

def get_player_name():
    name = ""
    while True:
        screen.fill(theme["background"])
        draw_text("NEW HIGH SCORE!", 30, theme["food"], WIDTH // 2, HEIGHT // 4)
        draw_text("Enter your name:", 24, theme["text"], WIDTH // 2, HEIGHT // 2 - 30)
        draw_text(name, 24, theme["text"], WIDTH // 2, HEIGHT // 2 + 10)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 15:
                    name += event.unicode

def game_over_screen(score, high_name, high_score):
    while True:
        screen.fill(theme["background"])
        draw_text("GAME OVER", 40, theme["food"], WIDTH // 2, HEIGHT // 4)
        draw_text(f"Your Score: {score}", 24, theme["text"], WIDTH // 2, HEIGHT // 2 - 20)
        draw_text(f"High Score: {high_name} - {high_score}", 24, theme["text"], WIDTH // 2, HEIGHT // 2 + 10)
        draw_text("Press ENTER to Return to Menu", 20, theme["text"], WIDTH // 2, HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return

def win_screen(score, high_name, high_score):
    if score > high_score:
        name = get_player_name()
        save_high_score(name, score)
        high_name, high_score = name, score

    while True:
        screen.fill(theme["background"])
        draw_text("YOU WIN!", 40, theme["snake"], WIDTH // 2, HEIGHT // 3)
        draw_text(f"Your Score: {score}", 24, theme["text"], WIDTH // 2, HEIGHT // 2)
        draw_text(f"High Score: {high_name} - {high_score}", 24, theme["text"], WIDTH // 2, HEIGHT // 2 + 40)
        draw_text("Press ENTER to return to menu", 24, theme["text"], WIDTH // 2, HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return


def load_level(index):
    path = f"levels/level{index}.txt"
    obstacles, anim_obs = [], []
    start, food = (CELL_SIZE, CELL_SIZE), None

    if not os.path.exists(path):
        return start, food, obstacles, anim_obs, 0, 0

    with open(path) as f:
        lines = f.readlines()

    level_height = len(lines)
    level_width = max(len(line.strip()) for line in lines) if lines else 0

    for row, line in enumerate(lines):
        for col, char in enumerate(line.strip()):
            x, y = col * CELL_SIZE, row * CELL_SIZE
            if char == "#":
                obstacles.append((x, y))
            elif char == "*":
                anim_obs.append((x, y))
            elif char == "S":
                start = (x, y)
            elif char == "F":
                food = (x, y)

    return start, food, obstacles, anim_obs, level_width, level_height

def get_all_free_positions(snake, obstacles, anim_obs, level_width, level_height):
    free_positions = []
    for x in range(0, level_width * CELL_SIZE, CELL_SIZE):
        for y in range(0, level_height * CELL_SIZE, CELL_SIZE):
            pos = (x, y)
            if pos not in obstacles and pos not in anim_obs and pos not in snake:
                free_positions.append(pos)
    return free_positions

def random_free_position(snake, obstacles, anim_obs, level_width, level_height):
    free_positions = get_all_free_positions(snake, obstacles, anim_obs, level_width, level_height)
    if free_positions:
        return random.choice(free_positions)
    else:

        return (CELL_SIZE, CELL_SIZE)

def main_game():
    level = START_LEVEL
    score = 0
    high_name, high_score = load_high_score()

    while level <= LEVELS_TO_WIN:
        start, fixed_food, obstacles, anim_obs, level_w, level_h = load_level(level)
        snake = [start]
        direction = (CELL_SIZE, 0)
        food = fixed_food if fixed_food else random_free_position(snake, obstacles, anim_obs, level_w, level_h)
        food_eaten = 0
        blink_timer = 0
        blink_on = True

        while True:
            clock.tick(FPS)
            blink_timer += 1
            if blink_timer % 15 == 0:
                blink_on = not blink_on

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
                not (0 <= head[0] < level_w * CELL_SIZE and 0 <= head[1] < level_h * CELL_SIZE) or
                head in obstacles or
                (blink_on and head in anim_obs)
            ):
                death_sound.play()
                if score > high_score:
                    name = get_player_name()
                    save_high_score(name, score)
                    high_name, high_score = name, score
                game_over_screen(score, high_name, high_score)
                return

            if head == food:
                food_sound.play()
                score += 1
                food_eaten += 1
                if food_eaten >= FOOD_PER_LEVEL:
                    break
                food = random_free_position(snake, obstacles, anim_obs, level_w, level_h)
            else:
                snake.pop()

            screen.fill(theme["background"])
            for obs in obstacles:
                draw_block(theme["obstacle"], obs)
            if blink_on:
                for obs in anim_obs:
                    draw_block(theme["animated_obstacle"], obs)
            for segment in snake:
                draw_block(theme["snake"], segment)
            draw_block(theme["food"], food)

            draw_text(f"Score: {score}", 20, theme["text"], 10, 10, center=False)
            pygame.display.update()

        level += 1

    win_screen(score, high_name, high_score)

# ===== Main Loop =====
while True:
    name, score = load_high_score()
    main_menu(name, score)
    main_game()
