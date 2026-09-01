from settings import *
from support import *
from timed import Timer
from monsters import *
from random import choice, sample
from ui import *
from attack import AttackAnimationSprite
import asyncio

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.set_num_channels(16)
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Catchom')
        self.clock = pygame.time.Clock()
        self.running = True
        self.import_assets()
        self.audio['music'].play(-1)
        self.all_sprites = pygame.sprite.Group()
        
        self.title_font = pygame.font.Font(join('code', 'font', 'font.ttf'), 80)
        self.button_font = pygame.font.Font(join('code', 'font', 'font.ttf'), 40)
        self.label_font = pygame.font.Font(join('code', 'font', 'font.ttf'), 26)
        self.gameover_font = pygame.font.Font(join('code', 'font', 'font.ttf'), 90)
        self.start_button_rect = pygame.Rect(0, 0, 260, 80)
        self.start_button_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100)
        self.play_again_rect = pygame.Rect(0, 0, 320, 80)
        self.play_again_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100)
        self.player_active = True
        self.state = 'start'
        self.opponent_defeated = 0

    def start_run(self):
        self.all_sprites.empty()
        self.opponent_defeated = 0
        player_monster_list = sample(list(MONSTER_DATA.keys()), 3)
        self.player_monsters = [Monster(name, self.back_surfs[name]) for name in player_monster_list]
        card_w, card_h, spacing = 260, 320, 60
        total_w = card_w * len(self.player_monsters) + spacing * (len(self.player_monsters) - 1)
        start_x = WINDOW_WIDTH / 2 - total_w / 2
        self.selection_rects = {}
        for i, monster in enumerate(self.player_monsters):
            rect = pygame.Rect(start_x + i * (card_w + spacing), WINDOW_HEIGHT / 2 - card_h / 2, card_w, card_h)
            self.selection_rects[monster.name] = rect
        self.state = 'select'

    def selection_monster(self, monster):
        self.monster = monster
        self.all_sprites.add(self.monster)
        opponent_name = choice(list(MONSTER_DATA.keys()))
        self.opponent = Opponent(opponent_name, self.front_surfs[opponent_name], self.all_sprites)
        self.ui = UI(self.monster, self.player_monsters, self.simple_surfs, self.get_input)
        self.opponent_ui = OpponentUI(self.opponent)
        self.timers = {'player end': Timer(1000, func = self.opponent_turn), 'opponent end': Timer(1000, func = self.player_turn)}
        self.player_active = True
        self.state = 'battle'

    def get_input(self, state, data = None):
        if state == 'attack':
            self.apply_attack(self.opponent, data)
        elif state == 'heal':
            self.monster.health += 50
            AttackAnimationSprite(self.monster, self.attack_frames['green'], self.all_sprites)
            self.audio['green'].play()
        elif state == 'switch':
            self.monster.kill()
            self.monster = data
            self.all_sprites.add(self.monster)
            self.ui.monster = self.monster 
        elif state == 'escape':
            self.state = 'escape'
            return
        self.player_active = False
        self.timers['player end'].activate()

    def apply_attack(self, target, attack):
        attack_data = ABILITIES_DATA[attack]
        attack_multiplier = ELEMENT_DATA[attack_data['element']][target.element]
        target.health -= attack_data['damage'] * attack_multiplier
        AttackAnimationSprite(target, self.attack_frames[attack_data['animation']], self.all_sprites)
        self.audio[attack_data['animation']].play()

    def opponent_turn(self):
        if self.opponent.health <= 0:
            self.player_active = True
            self.opponent.kill()
            self.opponent_defeated += 1
            if self.opponent_defeated >= 5:
                self.state = 'win'
                return
            monster_name = choice(list(MONSTER_DATA.keys()))
            self.opponent = Opponent(monster_name, self.front_surfs[monster_name], self.all_sprites)
            self.opponent_ui.monster = self.opponent
        attack = choice(self.opponent.abilities)
        self.apply_attack(self.monster, attack)
        self.timers['opponent end'].activate()

    def player_turn(self):
        self.player_active = True
        if self.monster.health <= 0:
            available_monsters = [monster for monster in self.player_monsters if monster.health > 0]
            if available_monsters:
                self.monster.kill()
                self.monster = available_monsters[0]
                self.all_sprites.add(self.monster)
                self.ui.monster = self.monster
            else:
                self.state = 'lose'

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def import_assets(self):
        self.back_surfs = folder_importer('code', 'images', 'back')
        self.front_surfs = folder_importer('code', 'images', 'front')
        self.bg_surfs = folder_importer('code', 'images', 'other')
        self.bg_surfs['bg'] = pygame.transform.scale(self.bg_surfs['bg'], (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.simple_surfs = folder_importer('code', 'images', 'simple')
        self.attack_frames = title_importer(4, 'code', 'images', 'attacks')
        self.audio = audio_importer('code', 'audio')

    def draw_monster_floor(self):
        for sprite in self.all_sprites:
            if isinstance(sprite, Creature):
                floor_rect = self.bg_surfs['floor'].get_frect(center = sprite.rect.midbottom + pygame.Vector2(0, -10))
                self.display_surface.blit(self.bg_surfs['floor'], floor_rect)

    def draw_start_screen(self):
        title_surf = self.title_font.render('Catchom', True, COLORS['black'])
        title_rect = title_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 60))
        self.display_surface.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        hovering = self.start_button_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.display_surface, COLORS['white'], self.start_button_rect, 0, 20)
        pygame.draw.rect(self.display_surface, COLORS['black'] if hovering else COLORS['gray'], self.start_button_rect, 4 , 20)

        start_surf = self.button_font.render('START', True, COLORS['black'])
        start_rect = start_surf.get_frect(center = self.start_button_rect.center)
        self.display_surface.blit(start_surf, start_rect)

    def draw_select_screen(self):
        prompt_surf = self.button_font.render('Choose your starter', True, COLORS['black'])
        prompt_rect = prompt_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 260))
        self.display_surface.blit(prompt_surf, prompt_rect)

        mouse_pos = pygame.mouse.get_pos()
        for monster in self.player_monsters:
            rect = self.selection_rects[monster.name]
            hovering = rect.collidepoint(mouse_pos)
            pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 20)
            pygame.draw.rect(self.display_surface, COLORS['black'] if hovering else COLORS['gray'], rect, 4, 20)

            sprite_surf = self.back_surfs[monster.name]
            sprite_rect = sprite_surf.get_frect(center = (rect.centerx, rect.centery - 40))
            self.display_surface.blit(sprite_surf, sprite_rect)

            name_surf = self.label_font.render(monster.name, True, COLORS['black'])
            name_rect = name_surf.get_frect(center = (rect.centerx, rect.bottom - 70))
            self.display_surface.blit(name_surf, name_rect)

            element_surf = self.label_font.render(monster.element.capitalize(), True, COLORS['gray'])
            element_rect = element_surf.get_frect(center = (rect.centerx, rect.bottom - 40))
            self.display_surface.blit(element_surf, element_rect)

    def draw_end_screen(self, text, color):
        title_surf = self.gameover_font.render(text, True, color)                
        title_rect = title_surf.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 80))
        self.display_surface.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        hovering = self.play_again_rect.collidepoint(mouse_pos)
        pygame.draw.rect(self.display_surface, COLORS['white'], self.play_again_rect, 0, 20)
        pygame.draw.rect(self.display_surface, COLORS['black'] if hovering else COLORS['gray'], self.play_again_rect, 4, 20)

        play_again_surf = self.button_font.render('PLAY AGAIN', True, COLORS['black'])
        play_again_text_rect = play_again_surf.get_frect(center = self.play_again_rect.center)
        self.display_surface.blit(play_again_surf, play_again_text_rect)

    def draw_win_screen(self):
            self.draw_end_screen('YOU WIN!', COLORS['black'])

    def draw_lose_screen(self):
            self.draw_end_screen('GAME OVER', COLORS['gray'])

    def draw_escape_screen(self):
        self.draw_end_screen('AWW MAN...', COLORS['gray'])

    async def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == 'start' and self.start_button_rect.collidepoint(event.pos):
                        self.start_run()

                    elif self.state == 'select':
                        for name, rect in self.selection_rects.items():
                            if rect.collidepoint(event.pos):
                                chosen = next(m for m in self.player_monsters if m.name == name)
                                self.selection_monster(chosen)
                                break

                    elif self.state in ('lose', 'win', 'escape') and self.play_again_rect.collidepoint(event.pos):
                        self.start_run()

            if self.state == 'battle':
                self.update_timers()
                self.all_sprites.update(dt)
                if self.player_active:
                    self.ui.update()

            self.display_surface.blit(self.bg_surfs['bg'], (0, 0))

            if self.state == 'start':
                self.draw_start_screen()
            elif self.state == 'select':
                self.draw_select_screen()
            elif self.state == 'battle':
                self.draw_monster_floor()
                self.all_sprites.draw(self.display_surface)
                self.ui.draw()
                self.opponent_ui.draw()
            elif self.state == 'lose':
                self.draw_lose_screen()
            elif self.state == 'win':
                self.draw_win_screen()
            elif self.state == 'escape':
                self.draw_escape_screen()

            pygame.display.update()
            await asyncio.sleep(0)

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    asyncio.run(game.run())