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


clock = pygame.time.Clock()

gameloop = True
current_screen: ScreenType = ScreenType.HOMESCREEN


def homescreen():
    display.blit(bg_image, (0, 0))
    size = display.get_size()
    title_font = pygame.font.SysFont("Arial", 130, False, False)
    button_font = pygame.font.SysFont("Arial", 64, False, False)

    button("Start", size[0]/2+size[0]/9, size[1]/2-size[1]/10, size[0]/8, size[1]/8, GREEN, GREEN_2, button_font, BLACK, 1, start_button)
    button("Quit", size[0]/2+size[0]/9, size[1]/2+size[1]/32, size[0]/8, size[1]/8, RED, RED_2, button_font, BLACK, 1, quit_button)

    title = title_font.render("Fynns Wurzelanfall", False, BLACK)

    display.blit(title, (size[0]/3-size[0]/8, size[1]/4.7))


height = 30
width = 30

def main_game():
    display_size = display.get_size()
    size_of_one = int((display_size[1]-display_size[1]/10)/height)
    for i in range(height):
        for j in range(width):
            pygame.draw.rect(display, BLACK, (i*size_of_one+display_size[1]/20, j*size_of_one+display_size[1]/20, size_of_one, size_of_one), 1)

    button_font = pygame.font.SysFont("Arial", 32, False, False)

    button("Home Screen", display_size[0]-display_size[0]/4, display_size[1]-(display_size[1]/32)*31, display_size[0]/8, display_size[1]/8, RED, RED_2, button_font, BLACK, 1, x_offset=-(display_size[0]/48), action=main_menu_button)


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


while gameloop:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            gameloop = False

    display.fill(color=BACKGROUND)

    if current_screen == ScreenType.HOMESCREEN:
        homescreen()
    elif current_screen == ScreenType.MAIN_GAME:
        main_game()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit(0)
