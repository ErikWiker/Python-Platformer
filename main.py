import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
#dynamically loading sprite sheets, we will be using a function for this (like animations)

pygame.init()

pygame.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800 #depends on monitor size
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def get_background():
    pass

#this is where you will handle the event loop
def main(window):
    clock = pygame.time.Clock()
    
    run = True
    while run:
        clock.tick(FPS) #ensures while loop will run no more than 60 FPS (slower PCs could be slower)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
    
    pygame.quit()
    quit()
            

#so we only call the main function if we run this file directly, not if we import something the file
if __name__ == "__main__": 
        main(window)