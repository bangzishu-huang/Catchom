from settings import *

class UI:
    def __init__(self, monster):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 30)
        self.left = WINDOW_WIDTH / 2 - 100
        self.top = WINDOW_HEIGHT / + 50
        self.monster = monster

        self.general_options = ['attack', 'heal', 'switch', 'escape']
        self.general_index = {'col': 0, 'row': 0}

    def input(self):
        keys = pygame.key.get_just_pressed()
        self.general_index['row'] += int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.general_index['col'] += int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        print(self.general_index)

    def general(self):
        rect = pygame.FRect(self.left - 10 , self.top + 420, 500, 300)
        pygame.draw.rect(self.display_surface, COLORS['white'], rect, 0, 4)
        pygame.draw.rect(self.display_surface, COLORS['gray'], rect, 4, 4)

        cols, rows = 2, 2
        for col in range(cols):
            for row in range(rows):
                x = rect.left + rect.width / 4 + (rect.width / 2) * col
                y = rect.top + rect.height / 4 + (rect.height / 2) * row
                i = col + 2 * row
                text_surf = self.font.render(self.general_options[i], True, 'black')
                text_rect = text_surf.get_frect(center = (x, y))
                self.display_surface.blit(text_surf, text_rect)

    def update(self):
        self.input()

    def draw(self):
        self.general()