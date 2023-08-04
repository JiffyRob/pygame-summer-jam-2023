import pygame
import player
from bush import asset_handler
# TODO: import assets here...


class Game:
    SIZE = pygame.Vector2(320, 240)
    FLAGS = pygame.SCALED | pygame.RESIZABLE
    BG_COLOR = 'blue'
    FPS = 30
    VSYNC = True

    def __init__(self):
        self.screen = None
        self.clock = pygame.time.Clock()
        self.running = False
        self.stack = []
        self.player = player.Player(self.SIZE / 2)


    def quit(self):
        self.running = False

    def run(self):
        self.running = True
        self.screen = pygame.display.set_mode(self.SIZE, self.FLAGS, self.VSYNC)
        self.clock.tick()
        dt = 0

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.player.handle_event(event)

            self.screen.fill(self.BG_COLOR)
            self.player.update(dt)
            self.screen.blit(self.player.image, self.player.rect.topleft)
            pygame.display.flip()
            dt = self.clock.tick(self.FPS) / 1000


if __name__ == "__main__":
    Game().run()
