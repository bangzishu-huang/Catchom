from settings import *

class Monster(pygame.sprite.Sprite):
    def __init__(self, name, surf) :
        super().__init__()
        self.image = surf
        self.rect = self.image.get_frect(bottomleft = (100, WINDOW_HEIGHT))
        self.name = name