import pygame
from settings import *

pygame.init()
font = pygame.font.SysFont("calibri", 20)


def debug(info, y=10, x=screen_width - 10):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, 'white')
    debug_rect = debug_surf.get_rect(topright=(x, y))
    display_surface.blit(debug_surf, debug_rect)
