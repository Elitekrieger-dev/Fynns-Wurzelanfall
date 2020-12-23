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

display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fynns Wurzelanfall")


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

    def __init__(self, _init_coordinates, _init_direction):
        self.fields = [_init_coordinates]
        self.direction = _init_direction
        self.increase_length = 3

    def move(self):
        if len(self.fields) > 1:
            if self.increase_length == 0:
                self.fields.pop(0)
            else:
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
        elif self.increase_length > 0:
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
        else:
            new_coordinates = list(self.fields[-1])
            if self.direction == Direction.UP:
                new_coordinates[1] -= 1
            elif self.direction == Direction.DOWN:
                new_coordinates[1] += 1
            elif self.direction == Direction.LEFT:
                new_coordinates[0] -= 1
            elif self.direction == Direction.RIGHT:
                new_coordinates[0] += 1#
            self.fields[0] = tuple(new_coordinates)

    def is_on_field(self, field):
        return field in self.fields


class FynnsWurzelanfall:
    def __init__(self, _height, _width):
        self.height = _height
        self.width = _width
        self.snake = Snake((15, 15), Direction.RIGHT)


clock = pygame.time.Clock()

gameloop = True
current_screen: ScreenType = ScreenType.HOMESCREEN


def homescreen(_):
    display.blit(bg_image, (0, 0))
    size = display.get_size()
    title_font = pygame.font.SysFont("Arial", 130, False, False)
    button_font = pygame.font.SysFont("Arial", 64, False, False)

    button("Start", size[0]/2+size[0]/9, size[1]/2-size[1]/10, size[0]/8, size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, start_button)
    button("Quit", size[0]/2+size[0]/9, size[1]/2+size[1]/32, size[0]/8, size[1]/8, RED, RED_2, button_font, BLACK, 1, quit_button)

    title = title_font.render("Fynns Wurzelanfall", False, BLACK)

    display.blit(title, (size[0]/3-size[0]/8, size[1]/4.7))


def main_game(_events):
    display_size = display.get_size()
    size_of_one = int((display_size[1]-display_size[1]/10)/game.height)
    for i in range(game.height):
        for j in range(game.width):
            if not game.snake.is_on_field((i, j)):
                pygame.draw.rect(display, BLACK, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20, size_of_one, size_of_one), 1)
            else:
                pygame.draw.rect(display, BLACK, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20, size_of_one, size_of_one))

    button_font = pygame.font.SysFont("Arial", 32, False, False)

    button("Home Screen", display_size[0]-display_size[0]/4, display_size[1]-(display_size[1]/32)*31, display_size[0]/8, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=-(display_size[0]/48), action=main_menu_button)
    global frame
    if frame >= 60:
        frame = 0
        game.snake.move()



def button(msg, x, y, w, h, ic, ac, font, color, button_id, action=None, x_offset=0, y_offset=0,  *args):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed(5)
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        pygame.draw.rect(display, ac, (x, y, w, h))

        if click[button_id-1] == 1 and action is not None:
            action(*args)
    else:
        pygame.draw.rect(display, ic, (x, y, w, h))

    text = font.render(msg, False, color)

    display.blit(text, (x + w/4 + x_offset, y + h/3 + y_offset))


def quit_button():
    global gameloop
    gameloop = False


def start_button():
    global current_screen
    current_screen = ScreenType.MAIN_GAME


def main_menu_button():
    global current_screen
    current_screen = ScreenType.HOMESCREEN


game = FynnsWurzelanfall(30, 30)

frame = 0

while gameloop:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            gameloop = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                game.snake.direction = Direction.DOWN
            elif event.key == pygame.K_UP:
                game.snake.direction = Direction.UP
            elif event.key == pygame.K_LEFT:
                game.snake.direction = Direction.LEFT
            elif event.key == pygame.K_RIGHT:
                game.snake.direction = Direction.RIGHT

    display.fill(color=BACKGROUND)

    if current_screen == ScreenType.HOMESCREEN:
        homescreen(events)
    elif current_screen == ScreenType.MAIN_GAME:
        main_game(events)

    pygame.display.update()
    frame += 1
    clock.tick(60)

pygame.quit()
sys.exit(0)
