import pygame
import time

from settings import *
from tiles import *
from player import Player
from camera import Camera
from game_data import levels
from support import import_csv_layout, import_cut_graphics
from spike import Spike
from light import Light

class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health, change_key, key_find):
        self.display_surface = surface
        self.current_x = 0
        
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        self.fog = pygame.Surface((screen_width, screen_height))
        self.fog.fill((255, 255, 255))

        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        fake_layout = import_csv_layout(level_data['fake_goal'])
        self.fake_goal = pygame.sprite.GroupSingle()
        fake_layout1 = import_csv_layout(level_data['fake_goal1'])
        self.fake_goal1 = pygame.sprite.GroupSingle()

        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(
            terrain_layout, 'terrain')

        jump_pads_layout = import_csv_layout(level_data['jump_pads'])
        self.jump_pad_sprites = self.create_tile_group(
            jump_pads_layout, 'jump_pads')

        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        key_layout = import_csv_layout(level_data['keys'])
        self.key_sprites = self.create_tile_group(key_layout, 'keys')

        torche_layout = import_csv_layout(level_data['torches'])
        self.torche_sprites = pygame.sprite.Group()

        spike_layout = import_csv_layout(level_data['spikes'])
        self.spike_sprites = self.create_tile_group(spike_layout, 'spikes')

        constraint_layout = import_csv_layout(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, 'constraints')

        self.change_coins = change_coins
        self.change_key = change_key
        self.change_health = change_health
        self.key_find = key_find

        total_level_width = len(terrain_layout[0]) * tile_size
        total_level_height = len(terrain_layout) * tile_size
        self.camera = Camera(self.complex_camera,
                             total_level_width, total_level_height)

        self.player_setup(player_layout, change_health)
        self.fake_goal_setup(fake_layout)
        self.fake_goal_setup1(fake_layout1)
        self.torche_setup(torche_layout, self.fog, self.camera)

        self.mouse_light = Light(pygame.mouse.get_pos()[
                                 0], pygame.mouse.get_pos()[1], 200, self.fog)

    def create_tile_group(self, layout, type):
        global sprite
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphics(
                            'graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    if type == 'jump_pads':
                        sprite = JumpPad(
                            tile_size, x, y, 'graphics/jump_pad/bounced')
                    if type == 'coins':
                        sprite = Coin(tile_size, x, y, 'graphics/coins')
                    if type == 'keys':
                        sprite = Key(tile_size, x, y, 'graphics/key/move')
                    if type == 'spikes':
                        if val == '0':
                            sprite = Spike(tile_size, x, y, 'vertical')
                        elif val == '1':
                            sprite = Spike(tile_size, x, y, 'horizontal')
                    if type == 'constraints':
                        sprite = Tile(tile_size, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    sprite = Player(
                        (x, y), self.display_surface, change_health)

                    self.player.add(sprite)
                if val == '1':
                    chess_surface = pygame.image.load(
                        'graphics/chess/chess__0.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, chess_surface)
                    self.goal.add(sprite)

    def fake_goal_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    fake_chess_surface = pygame.image.load(
                        'graphics/chess/chess__0.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, fake_chess_surface)
                    self.fake_goal.add(sprite)

    def fake_goal_setup1(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    fake_chess_surface1 = pygame.image.load(
                        'graphics/chess/chess__0.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, fake_chess_surface1)
                    self.fake_goal1.add(sprite)

    def torche_setup(self, layout, fog, camera):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == '0':
                    torche = Torche(tile_size, x, y,
                                    'graphics/torche/idle', 300, fog, camera)
                    self.torche_sprites.add(torche)

    def player_horizontal_collision(self, tiles):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed

        for sprite in tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        elif player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def player_vertical_collision(self, tiles):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in tiles.sprites():
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def complex_camera(self, camera, target_rect):
        x = -target_rect.center[0] + screen_width / 2
        y = -target_rect.center[1] + screen_height / 2
        camera.topleft += (pygame.Vector2((x, y)) -
                           pygame.Vector2(camera.topleft)) * 0.06
        camera.x = max(-(camera.width - screen_width), min(0, camera.x))
        camera.y = max(-(camera.height - screen_height), min(0, camera.y))

        return camera

    def check_win(self):
        collided_goal = pygame.sprite.spritecollide(
            self.player.sprite, self.goal, False)
        collided_fake_goal = pygame.sprite.spritecollide(
            self.player.sprite, self.fake_goal, False)
        collided_fake_goal1 = pygame.sprite.spritecollide(
            self.player.sprite, self.fake_goal1, False)
        if collided_goal and self.key_find():
            self.create_overworld(self.current_level, self.new_max_level)
        if collided_fake_goal and self.key_find():
            self.create_overworld(self.current_level, self.current_level)
        if collided_fake_goal1 and self.key_find():
            self.create_overworld(self.current_level, self.current_level)

    def check_jump_pad_collision(self):
        player = self.player.sprite
        collided_jump_pad = pygame.sprite.spritecollide(
            player, self.jump_pad_sprites, False)

        if collided_jump_pad:
            for jump_pad in collided_jump_pad:
                jump_pad_center = jump_pad.rect.centery
                jump_pad_top = jump_pad.rect.top
                player_bottom = player.rect.bottom

                if jump_pad_top < player_bottom < jump_pad_center and player.direction.y >= 0:
                    self.player.sprite.direction.y = -25

    def check_key_collision(self):
        collided_key = pygame.sprite.spritecollide(
            self.player.sprite, self.key_sprites, True)
        if collided_key:
            self.change_key(1)

    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(
            self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(1)

    def check_spike_collision(self):
        spike_collisions = pygame.sprite.spritecollide(
            self.player.sprite, self.spike_sprites, False)
        player = self.player.sprite

        if spike_collisions:
            player.get_damage()

    def spike_collision_reverse(self):
        for spike in self.spike_sprites.sprites():
            if pygame.sprite.spritecollide(spike, self.constraint_sprites, False):
                spike.reverse()

    def run(self):
        self.camera.update(self.player.sprite)
        
        for tile in self.terrain_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        for tile in self.jump_pad_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        self.player.update()
        self.player_horizontal_collision(self.terrain_sprites)
        self.player_vertical_collision(self.terrain_sprites)
        for tile in self.goal:
            self.display_surface.blit(tile.image, self.camera.apply(tile))
        for tile in self.fake_goal:
            self.display_surface.blit(tile.image, self.camera.apply(tile))
        for tile in self.fake_goal1:
            self.display_surface.blit(tile.image, self.camera.apply(tile))
        for player_sprite in self.player:
            self.display_surface.blit(
                player_sprite.image, self.camera.apply(player_sprite))

        self.torche_sprites.update()
        for sprite in self.torche_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        self.check_win()
        self.check_coin_collision()
        self.check_key_collision()
        self.check_spike_collision()
        self.check_jump_pad_collision()

        self.coin_sprites.update()
        for tile in self.coin_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        self.key_sprites.update()
        for tile in self.key_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        self.spike_sprites.update()
        self.constraint_sprites.update()
        self.spike_collision_reverse()
        for tile in self.spike_sprites:
            self.display_surface.blit(tile.image, self.camera.apply(tile))

        self.mouse_light.update()
        self.display_surface.blit(
            self.fog, (0, 0), special_flags=pygame.BLEND_MULT)
