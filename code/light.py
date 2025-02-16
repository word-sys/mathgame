import pygame


class Light(pygame.sprite.Sprite):
	def __init__(self, x, y, radius, surface):
		super().__init__()
		self.radius = radius
		self.display_surface = surface
		self.image = pygame.image.load('graphics/light_mask.png').convert_alpha()
		center_x = x + int(radius / 2)
		center_y = y + int(radius / 2)
		self.rect = self.image.get_rect(center=(center_x, center_y))
		self.image = pygame.transform.scale(self.image, (radius, radius))

	def update(self):
		self.display_surface.blit(self.image, self.rect)
