import random
from dataclasses import dataclass
from typing import Callable, Union

import errno
import json
import pygame
import sys
import os
from enum import Enum

BACKGROUND = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
RED_2 = (200, 0, 0)
GREEN = (0, 255, 0)
GREEN_2 = (0, 200, 0)
GRAY = (150, 150, 150)
GRAY_2 = (100, 100, 100)
GRAY_3 = (80, 80, 80)

FPS = 60
TICK_MULT = 2
TICK_TIME = FPS // TICK_MULT

HEIGHT = 30
WIDTH = 30

INIT_LENGTH = 3

POWERUP_1_SPAWN = TICK_MULT * 5
POWERUP_1_DESPAWN = TICK_MULT * 15

POWERUP_DESPAWN = TICK_TIME * 2

pygame.init()
pygame.font.init()

bg_image = pygame.image.load(r"assets\main_menu_background.png")
score_image = pygame.image.load(r"assets\Score.png")

power_up_1_image = pygame.image.load(r"assets\game_power_up_1.png")
despawn_image = pygame.image.load(r"assets\game_despawn.png")

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fynns Wurzelanfall")

SAVEGAME_PATH = os.path.join(os.getenv("appdata"), "Fynns Wurzelanfall/data/savegame.json")


class Setting(Enum):
    TEXT_ANTIALIAS = 0
    SIZE = 1


settings: dict[Setting, Union[int, float, bool]] = {
    Setting.TEXT_ANTIALIAS: True,
    Setting.SIZE: 30
}

temp: dict = {}


@dataclass
class PowerUp:
    on_collect: Callable[[], None]
    image: pygame.Surface
    despawn_time: int

    def new(self):
        return PowerUp(self.on_collect, self.image, self.despawn_time)


class ScreenType(Enum):
    HOMESCREEN = 0
    MAIN_GAME = 1
    END_SCREEN = 2
    SETTINGS = 3


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Snake:
    fields: list[tuple[int, int]]
    direction: Direction
    increase_length: int

    def __init__(self, _init_coordinates, _init_direction, _init_increase_length):
        self.init_coordinates = _init_coordinates
        self.init_direction = _init_direction
        self.init_increase_length = _init_increase_length
        self.fields = [_init_coordinates]
        self.direction = _init_direction
        self.increase_length = _init_increase_length
        self.decrease_length = 0

    def move(self):
        global current_screen
        if len(self.fields) == 0:
            self.reset()
            current_screen = ScreenType.HOMESCREEN
        if len(self.fields) > 1:
            if self.increase_length == 0:
                self.fields.pop(0)
            else:
                self.increase_length -= 1
            if self.decrease_length == 0:
                new_coordinates = list(self.fields[-1])
                if self.direction == Direction.UP:
                    new_coordinates[1] -= 1
                    new_coordinates[1] %= game.height
                elif self.direction == Direction.DOWN:
                    new_coordinates[1] += 1
                    new_coordinates[1] %= game.height
                elif self.direction == Direction.LEFT:
                    new_coordinates[0] -= 1
                    new_coordinates[0] %= game.width
                elif self.direction == Direction.RIGHT:
                    new_coordinates[0] += 1
                    new_coordinates[0] %= game.width
                self.fields.append(tuple(new_coordinates))
            else:
                self.decrease_length -= 1
        elif self.increase_length > 0 and self.decrease_length == 0:
            self.increase_length -= 1
            new_coordinates = list(self.fields[-1])
            if self.direction == Direction.UP:
                new_coordinates[1] -= 1
            elif self.direction == Direction.DOWN:
                new_coordinates[1] += 1
            elif self.direction == Direction.LEFT:
                new_coordinates[0] -= 1
            elif self.direction == Direction.RIGHT:
                new_coordinates[0] += 1
            self.fields.append(tuple(new_coordinates))
        elif self.increase_length > 0 and self.decrease_length > 0:
            self.increase_length -= 1
            self.decrease_length -= 1
        elif self.decrease_length > 0:
            self.decrease_length -= 1
            self.fields.pop(0)
        else:
            new_coordinates = list(self.fields[-1])
            if self.direction == Direction.UP:
                new_coordinates[1] -= 1
            elif self.direction == Direction.DOWN:
                new_coordinates[1] += 1
            elif self.direction == Direction.LEFT:
                new_coordinates[0] -= 1
            elif self.direction == Direction.RIGHT:
                new_coordinates[0] += 1
            self.fields[0] = tuple(new_coordinates)
        if len(set(self.fields)) != len(self.fields):
            reset()
            current_screen = ScreenType.END_SCREEN
        if self.fields[-1] in game.powerups.keys():
            game.powerups[self.fields[-1]][0].on_collect()
            game.powerups.pop(self.fields[-1])

    def reset(self):
        self.fields = [self.init_coordinates]
        self.direction = self.init_direction
        self.increase_length = self.init_increase_length
        self.decrease_length = 0

    def is_on_field(self, field):
        return field in self.fields


class FynnsWurzelanfall:
    def __init__(self, _height, _width, _init_x, _init_y, _start_length, _last_score=0):
        self.height = _height
        self.width = _width
        self.snake = Snake((_init_x, _init_y), Direction.RIGHT, _start_length-1)

        self.score = 0

        self.powerups: dict[tuple[int, int], list[Union[PowerUp, int]]] = {}

        self.despawn_coordinates = []

        self.powerup_1_spawn = POWERUP_1_SPAWN

        self.last_score = _last_score

    def spawn_power_up(self, powerup):
        pos = random.randint(0, self.width), random.randint(0, self.height)
        counter = 0
        while pos in self.powerups.keys() or pos in self.snake.fields:
            pos = random.randint(0, self.width), random.randint(0, self.height)
            counter += 1
            if counter > self.width * self.height * 4:
                reset()

        powerup = powerup.new()
        self.powerups |= {pos: [powerup, powerup.despawn_time]}

clock = pygame.time.Clock()

gameloop = True
current_screen: ScreenType = ScreenType.HOMESCREEN


def homescreen(_events):
    for event in _events:
        if event.type == pygame.QUIT:
            global gameloop
            gameloop = False
    display.blit(bg_image, (0, 0))
    size = display.get_size()
    title_font = pygame.font.SysFont("Arial", 130, False, False)
    button_font = pygame.font.SysFont("Arial", 64, False, False)
    settings_font = pygame.font.SysFont("Arial", 48, False, False)

    button("Start", size[0]/2+size[0]/9, size[1]/2-size[1]/10, size[0]/8, size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, action=start_button, antialias=settings[Setting.TEXT_ANTIALIAS])
    button("Quit", size[0]/2+size[0]/9, size[1]/2+size[1]/32, size[0]/8, size[1]/8, RED, RED_2, button_font, BLACK, 1, action=quit_button, antialias=settings[Setting.TEXT_ANTIALIAS])
    button("Settings", size[0]-size[0]/7, size[1]/32, size[0]/8, size[1]/8, GRAY, GRAY_2, settings_font, BLACK, 1, action=settings_button, antialias=settings[Setting.TEXT_ANTIALIAS], x_offset=size[0]/-64)

    text("Fynns Wurzelanfall", size[0]/3-size[0]/8, size[1]/4.7, title_font, BLACK, antialias=settings[Setting.TEXT_ANTIALIAS])


def main_game(_events):
    for event in _events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                game.snake.direction = Direction.DOWN
            elif event.key == pygame.K_UP:
                game.snake.direction = Direction.UP
            elif event.key == pygame.K_LEFT:
                game.snake.direction = Direction.LEFT
            elif event.key == pygame.K_RIGHT:
                game.snake.direction = Direction.RIGHT
    display_size = display.get_size()
    size_of_one = int((display_size[1]-display_size[1]/10)/game.height)
    for i in range(game.height):
        for j in range(game.width):
            if not game.snake.is_on_field((i, j)):
                pygame.draw.rect(display, BLACK, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20, size_of_one, size_of_one), 1)
            else:
                pygame.draw.rect(display, BLACK, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20, size_of_one, size_of_one))
            if (i, j) in game.powerups.keys():
                scaled_image = pygame.transform.scale(game.powerups[(i, j)][0].image, (size_of_one, size_of_one))
                display.blit(scaled_image, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20))
            if (i, j) in game.despawn_coordinates:
                scaled_image = pygame.transform.scale(despawn_image, (size_of_one, size_of_one))
                display.blit(scaled_image, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20))
                game.despawn_coordinates.remove((i, j))

    button_font = pygame.font.SysFont("Arial", 32, False, False)
    button("Home Screen", display_size[0]-display_size[0]/3.7, display_size[1]-(display_size[1]/32)*31, display_size[0]/8, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=-(display_size[0]/48), action=main_menu_button, antialias=settings[Setting.TEXT_ANTIALIAS])

    score_font = pygame.font.SysFont("Arial", 32, True, False)
    text("Score: " + str(game.score), display_size[0]-display_size[0]/4, display_size[1]-(display_size[1]/32)*16, score_font, BLACK, antialias=settings[Setting.TEXT_ANTIALIAS])
    text("High Score: " + str(save["highscore"]), display_size[0] - display_size[0] / 4,display_size[1] - (display_size[1] / 30) * 16, score_font, BLACK, antialias=settings[Setting.TEXT_ANTIALIAS])

    global frame
    if frame >= TICK_TIME:
        frame = 0
        game.snake.move()
        if game.powerup_1_spawn <= 0:
            game.powerup_1_spawn = POWERUP_1_SPAWN
            game.spawn_power_up(power_up_1)
        game.powerup_1_spawn -= 1
        to_remove = []
        for i in game.powerups.keys():
            game.powerups[i][1] -= 1
            if game.powerups[i][1] <= 0:
                to_remove.append(i)
        for i in to_remove:
            game.despawn_coordinates.extend([i] * POWERUP_DESPAWN)
            game.powerups.pop(i)


def endscreen(_):
    display_size = display.get_size()
    gameover_font = pygame.font.SysFont("Arial", 172, True, False)
    score_font = pygame.font.SysFont("Arial", 72, True, False)
    button_font = pygame.font.SysFont("Arial", 32, False, False)

    display.blit(score_image, (0, 0))

    text("GAME OVER", display_size[0]/2-display_size[0]/4, display_size[1]/2-display_size[1]/4, gameover_font, RED, antialias=settings[Setting.TEXT_ANTIALIAS])
    text(str(game.last_score), display_size[0]/2-display_size[0]/2.8, display_size[1]/2-display_size[1]/2.15, score_font, BLACK, antialias=settings[Setting.TEXT_ANTIALIAS])

    button("Home Screen", display_size[0]/2-display_size[0]/4, display_size[1]/1.2, display_size[0]/2, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=display_size[0]/15, action=main_menu_button_, antialias=settings[Setting.TEXT_ANTIALIAS])
    button("Play Again", display_size[0]/2-display_size[0]/4, display_size[1]/1.5, display_size[0]/2, display_size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, x_offset=display_size[0]/15, action=play_again_button, antialias=settings[Setting.TEXT_ANTIALIAS])

class SettingsTab(Enum):
    VIDEO = 0
    GAME = 1

def settings_screen(_):
    global temp
    if temp.get("antialias_timeout"):
        temp["antialias_timeout"] -= 1
    if temp.get("size_timeout"):
        temp["size_timeout"] -= 1

    def video():
        def antialias():
            def false():
                if temp.get("antialias_timeout") == 0 or temp.get("antialias_timeout") is None:
                    settings[Setting.TEXT_ANTIALIAS] = False
                temp["antialias_timeout"] = 2
            def true():
                if temp.get("antialias_timeout") == 0 or temp.get("antialias_timeout") is None:
                    settings[Setting.TEXT_ANTIALIAS] = True
                temp["antialias_timeout"] = 2
            value = settings[Setting.TEXT_ANTIALIAS]
            if value is False:
                button("Text Antialiasing", display_size[0]/32, display_size[1]/8, display_size[0]/4, display_size[1]/12, RED, RED_2, button_font, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=true)
            elif value is True:
                button("Text Antialiasing", display_size[0]/32, display_size[1]/8, display_size[0]/4, display_size[1]/12, GREEN, GREEN_2, button_font, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=false)
        antialias()

    def game_tab():
        def size():
            def inc():
                if temp.get("size_timeout") == 0 or temp.get("size_timeout") is None:
                    if settings[Setting.SIZE] < 100:
                        settings[Setting.SIZE] += 1
                temp["size_timeout"] = 2
            def dec():
                if temp.get("size_timeout") == 0 or temp.get("size_timeout") is None:
                    if settings[Setting.SIZE] > 5:
                        settings[Setting.SIZE] -= 1
                temp["size_timeout"] = 2
            button_font_ = pygame.font.SysFont("Arial", 144, False, False)
            text_font = pygame.font.SysFont("Arial", 60, False, False)
            button("-", display_size[0] / 32, display_size[1] / 8, display_size[0] / 20, display_size[1] / 12, RED, RED_2, button_font_, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=dec, y_offset=-display_size[1]/14)
            text(f"Grid Size: {settings[Setting.SIZE]}", display_size[0] / 12, display_size[1] / 7.5, text_font, BLACK, antialias=settings[Setting.TEXT_ANTIALIAS])
            button("+", display_size[0] / 3.5, display_size[1] / 8, display_size[0] / 20, display_size[1] / 12, GREEN, GREEN_2, button_font_, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=inc, y_offset=-display_size[1]/17, x_offset=-display_size[0]/100)

        size()

    def set_tab_video():
        temp["settings_current_tab"] = SettingsTab.VIDEO
    def set_tab_game():
        temp["settings_current_tab"] = SettingsTab.GAME

    button_font = pygame.font.SysFont("Arial", 32, False, False)

    display_size = display.get_size()

    current_tab = temp.get("settings_current_tab") or SettingsTab.VIDEO

    button("Home Screen", display_size[0]/1.2, display_size[1]/1.2, display_size[0]/8, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=-(display_size[0]/48), action=main_menu_button, antialias=settings[Setting.TEXT_ANTIALIAS])
    button("Video", display_size[0]/32, display_size[1]/32, display_size[0]/12, display_size[1]/12, *(GRAY, GRAY_2) if not current_tab == SettingsTab.VIDEO else (GRAY_2, GRAY_3), button_font, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=set_tab_video)
    button("Game", display_size[0]/8.74, display_size[1]/32, display_size[0]/12, display_size[1]/12, *(GRAY, GRAY_2) if not current_tab == SettingsTab.GAME else (GRAY_2, GRAY_3), button_font, BLACK, 1, antialias=settings[Setting.TEXT_ANTIALIAS], action=set_tab_game)

    if current_tab == SettingsTab.VIDEO:
        video()
    if current_tab == SettingsTab.GAME:
        game_tab()


def button(msg, x, y, w, h, ic, ac, font, color, button_id, action=None, x_offset=0, y_offset=0, antialias=False, *args):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed(5)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(display, ac, (x, y, w, h))

        if click[button_id-1] == 1 and action is not None:
            action(*args)
    else:
        pygame.draw.rect(display, ic, (x, y, w, h))

    text_ = font.render(msg, antialias, color)

    display.blit(text_, (x + w/4 + x_offset, y + h/3 + y_offset))


def text(msg, x, y, font, color, antialias=False):
    text_ = font.render(msg, antialias, color)
    display.blit(text_, (x, y))


def quit_button():
    global gameloop
    gameloop = False


def start_button():
    global current_screen
    current_screen = ScreenType.MAIN_GAME


def main_menu_button():
    global current_screen
    reset()
    save_settings()
    save_savegame()
    current_screen = ScreenType.HOMESCREEN


def main_menu_button_():
    global current_screen
    current_screen = ScreenType.HOMESCREEN


def play_again_button():
    global current_screen
    current_screen = ScreenType.MAIN_GAME

def settings_button():
    global current_screen
    current_screen = ScreenType.SETTINGS


def on_power_up_1_collect():
    game.snake.increase_length += 1
    game.score += 1


def reset():
    global game
    game = FynnsWurzelanfall(settings[Setting.SIZE], settings[Setting.SIZE], settings[Setting.SIZE]//2, settings[Setting.SIZE]//2, INIT_LENGTH, _last_score=game.score)
    if game.last_score > save["highscore"]:
        save["highscore"] = game.last_score
        save_savegame()


def load_savegame():
    global save
    if os.path.exists(SAVEGAME_PATH):
        with open(SAVEGAME_PATH, "rb") as f:
            ssave = f.read().decode("utf-8")
            jsonsave = json.loads(ssave)
            for line in jsonsave.items():
                if not line[0] == "settings":
                    save |= {line[0]: line[1]}
        load_settings(jsonsave["settings"])
    else:
        try:
            os.makedirs(os.path.dirname(SAVEGAME_PATH))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
        with open(SAVEGAME_PATH, "wb") as f:
            f.write(json.dumps(save).encode("utf-8"))


def save_savegame():
    global save
    with open(SAVEGAME_PATH, "wb") as f:
        f.write(json.dumps(save).encode("utf-8"))


def parse_settings_to_json(_settings):
    ret = {}
    for i in _settings.items():
        ret |= {i[0].name: i[1]}
    return ret


def load_settings(_save):
    global settings
    for i in _save.copy().items():
        settings |= {Setting[i[0]]: i[1]}


def save_settings():
    save["settings"] = parse_settings_to_json(settings)


power_up_1 = PowerUp(on_power_up_1_collect, power_up_1_image, POWERUP_1_DESPAWN)

save = {
    "highscore": 0,
    "settings": parse_settings_to_json(settings)
}

load_savegame()
save_savegame()

game = FynnsWurzelanfall(settings[Setting.SIZE], settings[Setting.SIZE], settings[Setting.SIZE]//2, settings[Setting.SIZE]//2, INIT_LENGTH)


frame = 0

while gameloop:
    events = pygame.event.get()

    display.fill(color=BACKGROUND)

    for e in events:
        if e.type == pygame.QUIT:
            gameloop = False

    if current_screen == ScreenType.HOMESCREEN:
        homescreen(events)
    elif current_screen == ScreenType.MAIN_GAME:
        main_game(events)
    elif current_screen == ScreenType.END_SCREEN:
        endscreen(events)
    elif current_screen == ScreenType.SETTINGS:
        settings_screen(events)

    pygame.display.update()
    frame += 1
    clock.tick(FPS)

pygame.quit()
sys.exit(0)
