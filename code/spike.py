import pygame
from tiles import AnimatedTile, StaticTile
from random import randint


class Spike(AnimatedTile):
	def __init__(self, size, x, y, direction):
		super().__init__(size, x, y, 'graphics/spike/idle')
		center_x = x + int(size / 2)
		center_y = y + int(size / 2)
		self.rect = self.image.get_rect(center=(center_x, center_y))
		self.speed = randint(2, 6)
		self.angle = 0
		self.direction = direction

	def move(self):
		if self.direction == 'vertical':
			self.rect.x += self.speed
		else:
			self.rect.y += self.speed
		self.angle += 4

	def rotate(self):
		if self.angle >= 360:
			self.angle = 0

		self.image = pygame.transform.rotate(self.image, self.angle)

	def reverse(self):
		self.speed *= -1

	def update(self):
		self.animate()
		self.move()
		# self.rotate()

