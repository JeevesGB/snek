import pygame
import sys
import os
import json
import random

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ====== Load Settings ======
DEFAULT_SETTINGS = {
    "width": 900,
    "height": 600,
    "cell_size": 22,
    "fps": 6,
    "start_level": 1,
    "levels_to_win": 3,
    "food_per_level": 5,
    "music_enabled": True
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
music_enabled = settings.get("music_enabled", True)

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
        with open(resource_path("theme.json"), "r") as f:
            user_theme = json.load(f)
            return {**DEFAULT_THEME, **user_theme}
    except:
        return DEFAULT_THEME

theme = load_theme()

# ====== Init ======
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("comic sans", 24)

# ====== Load sounds ======
death_sound = pygame.mixer.Sound(resource_path("audio/deathsound.mp3"))
food_sound = pygame.mixer.Sound(resource_path("audio/foodpickup.mp3"))

# ====== Load music ======
def play_music(filename):
    if music_enabled:
        pygame.mixer.music.load(resource_path(os.path.join("audio", filename)))
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()

def stop_music():
    pygame.mixer.music.stop()

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        pygame.mixer.music.set_volume(1.0)
    else:
        pygame.mixer.music.set_volume(0.0)

# ====== Load Images ======
def load_image(path):
    try:
        img = pygame.image.load(resource_path(path)).convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except:
        return None

snake_head_img = load_image(os.path.join("img", "player.png"))
snake_body_img = load_image(os.path.join("img", "playerbody.png"))

HIGH_SCORE_FILE = "highscore.txt"

def load_high_score():
    path = resource_path(HIGH_SCORE_FILE)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                line = f.read().strip()
                if ":" in line:
                    name, score = line.split(":")
                    return name.strip(), int(score.strip())
            except:
                return "", 0
    return "", 0

def save_high_score(name, score):
    with open(resource_path(HIGH_SCORE_FILE), "w") as f:
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

def difficulty_menu():
    while True:
        screen.fill(theme["background"])
        draw_text("CHOOSE DIFFICULTY", 36, theme["snake"], WIDTH // 2, HEIGHT // 4)
        draw_text("1 - Normal (3 Lives)", 28, theme["text"], WIDTH // 2, HEIGHT // 2 - 20)
        draw_text("2 - Hard (1 Life)", 28, theme["text"], WIDTH // 2, HEIGHT // 2 + 20)
        draw_text("Press 1 or 2", 20, theme["text"], WIDTH // 2, HEIGHT - 60)
        draw_text("M to toggle music", 18, theme["text"], 10, HEIGHT - 30, center=False)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 3
                elif event.key == pygame.K_2:
                    return 1
                elif event.key == pygame.K_m:
                    toggle_music()

def main_menu(high_name, high_score):
    play_music("menu.wav")
    while True:
        screen.fill(theme["background"])
        draw_text("SNAKE GAME", 40, theme["snake"], WIDTH // 2, HEIGHT // 4)
        draw_text("Press ENTER to Start", 24, theme["text"], WIDTH // 2, HEIGHT // 2)
        draw_text(f"High Score: {high_name} - {high_score}", 20, theme["text"], WIDTH // 2, HEIGHT - 40)
        draw_text("M to toggle music", 18, theme["text"], 10, HEIGHT - 30, center=False)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_m:
                    toggle_music()

# Placeholder implementations

def get_player_name():
    return "Player"

def game_over_screen(score, high_name, high_score):
    draw_text("Game Over", 40, theme["food"], WIDTH // 2, HEIGHT // 2 - 40)
    draw_text(f"Score: {score}", 28, theme["text"], WIDTH // 2, HEIGHT // 2)
    draw_text(f"High Score: {high_name} - {high_score}", 24, theme["text"], WIDTH // 2, HEIGHT // 2 + 40)
    pygame.display.flip()
    pygame.time.wait(3000)

def win_screen(score):
    draw_text("You Win!", 40, theme["snake"], WIDTH // 2, HEIGHT // 2 - 40)
    draw_text(f"Final Score: {score}", 28, theme["text"], WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    pygame.time.wait(3000)

def load_level(level):
    level_file = resource_path(os.path.join("levels", f"level{level}.txt"))

    start = (CELL_SIZE * 5, CELL_SIZE * 5)
    fixed_food = None
    obstacles = []
    animated_obstacles = []

    if not os.path.exists(level_file):
        print(f"Level file {level_file} not found. Using default empty level.")
        return start, fixed_food, obstacles, animated_obstacles, COLS, ROWS

    with open(level_file, "r") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]

    for row_idx, line in enumerate(lines):
        for col_idx, char in enumerate(line):
            pos = (col_idx * CELL_SIZE, row_idx * CELL_SIZE)
            if char == "#":
                obstacles.append(pos)
            elif char == "A" or char == "*":  
                animated_obstacles.append(pos)
            elif char == "S":
                start = pos
            elif char == "F":
                fixed_food = pos

    level_w = max(len(line) for line in lines)
    level_h = len(lines)

    return start, fixed_food, obstacles, animated_obstacles, level_w, level_h



def random_free_position(snake, obstacles, anim_obs, level_w, level_h):
    while True:
        pos = (random.randint(0, level_w - 1) * CELL_SIZE, random.randint(0, level_h - 1) * CELL_SIZE)
        if pos not in snake and pos not in obstacles and pos not in anim_obs:
            return pos

def main_game():
    play_music("gamemusic.wav")
    high_name, high_score = load_high_score()
    lives = difficulty_menu()
    score = 0
    level = START_LEVEL

    while level <= LEVELS_TO_WIN:
        while True:
            start, fixed_food, obstacles, anim_obs, level_w, level_h = load_level(level)
            snake = [start]
            direction = (CELL_SIZE, 0)
            food = fixed_food if fixed_food else random_free_position(snake, obstacles, anim_obs, level_w, level_h)
            food_eaten = 0
            blink_timer = 0
            blink_on = True
            level_complete = False

            while not level_complete:
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
                        elif event.key == pygame.K_m:
                            toggle_music()

                head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
                snake.insert(0, head)

                if (
                    head in snake[1:] or
                    not (0 <= head[0] < level_w * CELL_SIZE and 0 <= head[1] < level_h * CELL_SIZE) or
                    head in obstacles or
                    (blink_on and head in anim_obs)
                ):
                    death_sound.play()
                    lives -= 1
                    if lives <= 0:
                        if score > high_score:
                            name = get_player_name()
                            save_high_score(name, score)
                        game_over_screen(score, high_name, high_score)
                        return
                    else:
                        break

                if head == food:
                    food_sound.play()
                    score += 1
                    food_eaten += 1
                    if food_eaten >= FOOD_PER_LEVEL:
                        level_complete = True
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
                for i, segment in enumerate(snake):
                    if i == 0 and snake_head_img:
                        screen.blit(snake_head_img, segment)
                    elif i > 0 and snake_body_img:
                        screen.blit(snake_body_img, segment)
                    else:
                        draw_block(theme["snake"], segment)
                draw_block(theme["food"], food)

                draw_text(f"Score: {score}", 20, theme["text"], 10, 10, center=False)
                draw_text(f"Lives: {lives}", 20, theme["text"], WIDTH - 100, 10, center=False)
                pygame.display.update()

            if level_complete:
                level += 1
                break

    if score > high_score:
        name = get_player_name()
        save_high_score(name, score)
    win_screen(score)

# ===== Main Loop =====
while True:
    name, score = load_high_score()
    main_menu(name, score)
    main_game()
