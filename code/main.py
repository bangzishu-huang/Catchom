from settings import *
from support import *
from timed import Timer
from monsters import Monster, Opponent
from random import choice
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Catchom')
        self.clock = pygame.time.Clock()
        self.running = True
        self.import_assets()
        self.player_active = True
        self.all_sprites = pygame.sprite.Group()
        
        

        player_monster_list = ['Sparchu', 'Cleaf', 'Jacana', 'Gulfin', 'Pouch', 'Larvea']
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        self.monster = self.player_monsters[0]
        self.all_sprites.add(self.monster)
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)

        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.timers = {'player end': Timer(1000, func = self.opponent_turn), 'opponent end': Timer(1000, func = self.player_turn)}


    def get_input(self, state, data = None):
        if state == 'attack':
            self.apply_attack(self.opponent, data)
        elif state == 'escape':
            self.running = False
        self.player_active = False
        self.timers['player end'].activate()

    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        attack_multiplier = ELEMENT_DATA[attack_data['element']][target.element]
        target.health -= attack_data['damage'] * attack_multiplier
        print(f'{target.health}/{target.max_health}')

    def opponent_turn(self):
        attack = choice(self.opponent.abilities)
        self.apply_attack(self.monster, attack)
        self.timers['opponent end'].activate()

    def player_turn(self):
        self.player_active = True

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def import_assets(self):
        self.back_surfs = folder_importer('code', 'images', 'back')
        self.front_surfs = folder_importer('code', 'images', 'front')
        self.bg_surfs = folder_importer('code', 'images', 'other')
        self.bg_surfs['bg'] = pygame.transform.scale(self.bg_surfs['bg'], (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.simple_surfs = folder_importer('code', 'images', 'simple')

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            floor_rect = self.bg_surfs['floor'].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
            self.display_surface.blit(self.bg_surfs['floor'], floor_rect)

    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update_timers()
            self.all_sprites.update(dt)
            if self.player_active:
                self.ui.update()
            self.display_surface.blit(self.bg_surfs['bg'], (0, 0))
            self.draw_monster_floor()
            self.all_sprites.draw(self.display_surface)
            self.ui.draw()
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()