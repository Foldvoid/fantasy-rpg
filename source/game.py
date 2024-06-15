import sys

import source.interface as interface
from source.interface import pygame


running = False

def run():
    global running
    running = True
    print("Game is running.")

    while running:
        running = interface.eventHandle()
        interface.manageState()

    pygame.quit()
    sys.exit(0)
