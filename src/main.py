import pygame
from bush import asset_handler
# TODO: import assets here...


class Game:
    SIZE = (320, 240)
    FLAGS = pygame.SCALED | pygame.RESIZABLE
    BG_COLOR = 'blue'
    FPS = 30
    VSYNC = True

    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.stack = []


    def quit(self):
        self.running = False

    def run(self):
        self.running = True
        self.screen = pygame.display.set_mode(self.SIZE, self.FLAGS, self.VSYNC)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(self.BG_COLOR)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
