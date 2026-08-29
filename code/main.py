from settings import *
from support import *
from timer import *
from monster import Monster
class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Catchom')
        self.clock = pygame.time.Clock()
        self.running = True
        self.import_assets()
        self.all_sprites = pygame.sprite.Group()
        

        player_monster_list = ['Sparchu', 'Cleaf', 'Jacana']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]

    def import_assets(self):
        self.back_surfs = folder_importer('code', 'images', 'back')
        print(self.back_surfs)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.all_sprites.update(dt)
            self.all_sprites.draw(self.display_surface)
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()