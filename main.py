import random
from dataclasses import dataclass
from typing import Callable, Union

import pygame
import sys
from enum import Enum

BACKGROUND = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
RED_2 = (200, 0, 0)
GREEN = (0, 255, 0)
GREEN_2 = (0, 200, 0)

pygame.init()
pygame.font.init()

bg_image = pygame.image.load(r"assets\main_menu_background.png")
score_image = pygame.image.load(r"assets\Score.png")

power_up_1_image = pygame.image.load(r"assets\game_power_up_1.png")
despawn_image = pygame.image.load(r"assets\game_despawn.png")

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fynns Wurzelanfall")


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
            game.reset()
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
    def __init__(self, _height, _width, _init_x, _init_y, _start_length):
        self.height = _height
        self.width = _width
        self.snake = Snake((_init_x, _init_y), Direction.RIGHT, _start_length-1)

        self.score = 0

        self.powerups: dict[tuple[int, int], list[Union[PowerUp, int]]] = {}

        self.despawn_coordinates = []

        self.powerup_1_spawn = 10

        self.last_score = 0

    def spawn_power_up(self, powerup):
        pos = random.randint(0, self.width), random.randint(0, self.height)
        while pos in self.powerups.keys() or pos in self.snake.fields:
            pos = random.randint(0, self.width), random.randint(0, self.height)

        powerup = powerup.new()
        self.powerups |= {pos: [powerup, powerup.despawn_time]}

    def reset(self):
        self.last_score = self.score
        self.score = 0
        self.powerups = {}
        self.powerup_1_spawn = 10
        self.snake.reset()


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

    button("Start", size[0]/2+size[0]/9, size[1]/2-size[1]/10, size[0]/8, size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, start_button, antialias=True)
    button("Quit", size[0]/2+size[0]/9, size[1]/2+size[1]/32, size[0]/8, size[1]/8, RED, RED_2, button_font, BLACK, 1, quit_button, antialias=True)

    text("Fynns Wurzelanfall", size[0]/3-size[0]/8, size[1]/4.7, title_font, BLACK, antialias=True)


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
    button("Home Screen", display_size[0]-display_size[0]/4, display_size[1]-(display_size[1]/32)*31, display_size[0]/8, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=-(display_size[0]/48), action=main_menu_button, antialias=True)

    score_font = pygame.font.SysFont("Arial", 32, True, False)
    text("Score: " + str(game.score), display_size[0]-display_size[0]/4, display_size[1]-(display_size[1]/32)*16, score_font, BLACK, antialias=True)

    global frame
    if frame >= 30:
        frame = 0
        game.snake.move()
        if game.powerup_1_spawn <= 0:
            game.powerup_1_spawn = 10
            game.spawn_power_up(power_up_1)
        game.powerup_1_spawn -= 1
        to_remove = []
        for i in game.powerups.keys():
            game.powerups[i][1] -= 1
            if game.powerups[i][1] <= 0:
                to_remove.append(i)
        for i in to_remove:
            for _ in range(60):
                game.despawn_coordinates.append(i)
            game.powerups.pop(i)


def endscreen(_):
    display_size = display.get_size()
    gameover_font = pygame.font.SysFont("Arial", 172, True, False)
    score_font = pygame.font.SysFont("Arial", 72, True, False)
    button_font = pygame.font.SysFont("Arial", 32, False, False)

    display.blit(score_image, (0, 0))

    text("GAME OVER", display_size[0]/2-display_size[0]/4, display_size[1]/2-display_size[1]/4, gameover_font, RED, antialias=True)
    text(str(game.last_score), display_size[0]/2-display_size[0]/2.8, display_size[1]/2-display_size[1]/2.15, score_font, BLACK, antialias=True)

    button("Home Screen", display_size[0]/2-display_size[0]/4, display_size[1]/1.2, display_size[0]/2, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=display_size[0]/15, action=main_menu_button_, antialias=True)
    button("Play Again", display_size[0]/2-display_size[0]/4, display_size[1]/1.5, display_size[0]/2, display_size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, x_offset=display_size[0]/15, action=play_again_button, antialias=True)



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
    game.reset()
    current_screen = ScreenType.HOMESCREEN


def main_menu_button_():
    global current_screen
    current_screen = ScreenType.HOMESCREEN


def play_again_button():
    global  current_screen
    current_screen = ScreenType.MAIN_GAME


def on_power_up_1_collect():
    game.snake.increase_length += 1
    game.score += 1


power_up_1 = PowerUp(on_power_up_1_collect, power_up_1_image, 15*2)


game = FynnsWurzelanfall(30, 30, 15, 15, 3)

frame = 0

while gameloop:
    events = pygame.event.get()

    display.fill(color=BACKGROUND)

    if current_screen == ScreenType.HOMESCREEN:
        homescreen(events)
    elif current_screen == ScreenType.MAIN_GAME:
        main_game(events)
    elif current_screen == ScreenType.END_SCREEN:
        endscreen(events)

    pygame.display.update()
    frame += 1
    clock.tick(60)

pygame.quit()
sys.exit(0)
