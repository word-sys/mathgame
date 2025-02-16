import pygame
import sys

sys.path.append('code/')

from settings import *
from level import Level
from overworld import Overworld
from ui import UI
from debug import debug


class Game:
    def __init__(self):

        # Game attributes
        self.max_level = 0
        self.max_health = 200
        self.current_health = 200
        self.coins_amount = 0
        self.key_amount = 0

        # Overworld creation
        self.overworld = Overworld(
            0, self.max_level, screen, self.create_level)
        self.status = 'overworld'

        # User interface
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.key_amount = 0
        self.level = Level(current_level,
                           screen,
                           self.create_overworld,
                           self.change_coins,
                           self.change_health,
                           self.change_key,
                           self.key_find)
        self.status = 'level'

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(
            current_level, self.max_level, screen, self.create_level)
        self.status = 'overworld'

    def change_coins(self, amount):
        self.coins_amount += amount

    def change_health(self, amount):
        self.current_health += amount

    def change_key(self, amount):
        self.key_amount += amount

    def key_find(self):
        if self.key_amount == 1:
            return True
        else:
            return False

    def check_game_over(self):
        if self.current_health <= 0:
            self.key_amount = 0
            self.current_health = 200
            self.coins_amount = 0
            self.max_level = self.level.new_max_level
            self.status = 'overworld'

    def run(self):
        if self.status == 'overworld':
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins_amount)
            self.ui.show_key(self.key_amount)
            self.check_game_over()

pygame.init()

icon = pygame.image.load("graphics/icon.png")
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Math Game made by 9 Lives Studios")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
game = Game()

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('black')
    game.run()

    pygame.display.update()
    clock.tick(75)
