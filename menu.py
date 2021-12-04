import sys

import pygame
from Button import button

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('game')

X = 800
Y = 400

color = (53, 78, 203)
# set framerate
clock = pygame.time.Clock()
FPS = 60


BG = pygame.image.load('img/Icon/background.png').convert_alpha()


new_game = button(60, 155, 'New game')
Quit = button(60, 320, 'Quit')


run = True
while run:

    screen.blit(BG, (0, 0))

    clock.tick(FPS)

    if new_game.draw_button():
        exec(open("main.py").read())
        pygame.quit()
        sys.exit()

    if Quit.draw_button():
        run = False

    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()

pygame.quit()