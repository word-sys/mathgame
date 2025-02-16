import pygame
from settings import *
from game_data import levels
from level import Level

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path):
        super().__init__()
        self.image = pygame.image.load(path)
        if status == 'available':
            self.status = 'available'
            self.image.set_alpha(255)
        else:
            self.status = 'locked'
            self.image.set_alpha(100)
        self.rect = self.image.get_rect(center=pos)

        self.detection_zone = pygame.Rect(self.rect.centerx - (
            icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)


class Icon(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load(
            'graphics/overworld/select_icon.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.rect.center = self.pos


class Overworld:
    def __init__(self, start_level, max_level, surface, create_level):

        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        self.moving = False
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 10

        self.title = pygame.image.load('graphics/banner.png')
        self.title_rect = self.title.get_rect(topleft=(50, 0))

        self.selection = pygame.image.load('graphics/selection.png')
        self.selection_rect = self.title.get_rect(
            center=(screen_width - int(screen_width / 4), screen_height - 50))

        self.setup_nodes()
        self.setup_icon()

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(
                    node_data['node_pos'], 'available', self.speed, node_data['node_graphic'])
            else:
                node_sprite = Node(
                    node_data['node_pos'], 'locked', self.speed, node_data['node_graphic'])
            self.nodes.add(node_sprite)
    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[
                           self.current_level].rect.center)
        self.icon.add(icon_sprite)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data('next')
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_movement_data('previous')
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE]:
                self.create_level(self.current_level)

    def get_movement_data(self, target):
        start = pygame.math.Vector2(
            self.nodes.sprites()[self.current_level].rect.center)

        if target == 'next':
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level + 1].rect.center)
        else:
            end = pygame.math.Vector2(
                self.nodes.sprites()[self.current_level - 1].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def run(self):
        self.input()
        self.update_icon_pos()
        self.icon.update()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)

        self.display_surface.blit(self.title, self.title_rect)
        self.display_surface.blit(self.selection, self.selection_rect)
